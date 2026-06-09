#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cocomo_probe.py  —  objective repository-attribute extraction for COCOMO II synthesis
=====================================================================================
For each measured repo (from measurements_census.csv: repo_url + resolved_commit), clone
at the delivered commit and extract OBJECTIVE, reproducible signals that the COCOMO II
variable-synthesis rules consume (see docs/method/cocomoII_synthesis_spec.md). No subjective
judgement: every attribute is a deterministic function of files/dependencies in the repo.

Outputs data/calibration/repo_attributes.csv (one row per measured repo). Resumable: rows
already present are skipped unless --force.

Each attribute is a 0/1 flag or a small count/category, derived from:
  - file presence (CI, tests, docker, docs, audit/security, lint/format configs)
  - repo structure (on-chain: runtime/ + pallets/ ; contracts/ ; frontend share)
  - dependency manifests (Cargo.toml / package.json) scanned for blockchain-relevant libs:
      consensus (babe/grandpa/aura/sc-consensus), cross-chain (xcm/bridge/ibc/parachain),
      zk/crypto (ark-/halo2/circom/bellman/snark/plonk/bls/secp256k1/ed25519),
      smart-contract (solidity/ink!/pallet-contracts), frontend (react/vue/next/svelte)
"""
import argparse, csv, json, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
CACHE = HERE / "repo_cache"
EXCLUDE_DIRS = {"node_modules", "vendor", ".git", "dist", "build", "target",
                "__pycache__", ".venv", "venv", "third_party", "thirdparty"}

# dependency-name signals (substring match, case-insensitive) in manifest files
DEP_SIGNALS = {
    "consensus": ["sc-consensus", "sp-consensus", "babe", "grandpa", "aura", "pow", "pos-",
                  "tendermint", "hotstuff", "narwhal", "bullshark"],
    "crosschain": ["xcm", "cumulus", "parachain", "polkadot-parachain", "ibc", "bridge",
                   "snowbridge", "hyperlane", "layerzero", "wormhole"],
    "zkcrypto": ["ark-", "arkworks", "halo2", "circom", "bellman", "snark", "plonk", "groth16",
                 "bls12", "secp256k1", "ed25519", "schnorr", "merkle", "poseidon", "risc0", "zk"],
    "contract": ["solidity", "ink", "pallet-contracts", "solang", "hardhat", "foundry",
                 "openzeppelin", "ethers", "web3", "wasmi"],
    "frontend": ["react", "vue", "next", "svelte", "angular", "@polkadot/api", "wagmi", "viem"],
}

def _run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def ensure_clone(pid, repo_url):
    dest = CACHE / pid
    if (dest / ".git").exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = _run(["git", "clone", "--quiet", "--filter=blob:none", repo_url, str(dest)])
    if r.returncode != 0:
        r = _run(["git", "clone", "--quiet", repo_url, str(dest)])
    if r.returncode != 0:
        raise RuntimeError(f"clone failed: {r.stderr[:200]}")
    return dest

def checkout(dest, sha):
    if sha:
        _run(["git", "fetch", "--quiet", "origin", sha], cwd=dest)
        _run(["git", "checkout", "--quiet", "-f", sha], cwd=dest)

def walk_files(root):
    root = str(root)
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS]
        for fn in fns:
            full = os.path.join(dp, fn)
            yield os.path.relpath(full, root).replace("\\", "/").lower(), full

def probe(dest):
    paths = []; manifests = []
    # functional-size accumulators (blockchain "feature units" — countable from code AND
    # estimable from a design spec, so usable as a PROSPECTIVE COCOMO size driver)
    fs = dict(n_pallets=0, n_extrinsics=0, n_storage=0, n_events=0,
              n_ink_msgs=0, n_sol_funcs=0, n_contracts_def=0, n_rpc=0)
    MAX_BYTES = 600_000
    for rel, full in walk_files(dest):
        paths.append(rel)
        base = os.path.basename(rel)
        if base in ("cargo.toml", "package.json", "go.mod", "requirements.txt", "pyproject.toml",
                    "hardhat.config.js", "foundry.toml"):
            try:
                manifests.append(open(full, encoding="utf-8", errors="ignore").read().lower())
            except Exception:
                pass
        # functional-size: scan Rust (Substrate pallets / ink!) and Solidity sources
        if rel.endswith(".rs") or rel.endswith(".sol"):
            try:
                if os.path.getsize(full) > MAX_BYTES:
                    continue
                txt = open(full, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if rel.endswith(".rs"):
                fs["n_pallets"]       += txt.count("#[frame_support::pallet]") + txt.count("#[pallet::pallet]")
                fs["n_extrinsics"]    += txt.count("#[pallet::call_index")
                fs["n_storage"]       += txt.count("#[pallet::storage]")
                fs["n_events"]        += txt.count("#[pallet::event]")
                fs["n_ink_msgs"]      += txt.count("#[ink(message")
                fs["n_contracts_def"] += txt.count("#[ink::contract]") + txt.count("#[contract]")
                fs["n_rpc"]           += txt.count("#[rpc(") + txt.count("#[method(")
            else:  # .sol
                fs["n_sol_funcs"]     += len(re.findall(r"\bfunction\s+\w+", txt))
                fs["n_contracts_def"] += len(re.findall(r"\bcontract\s+\w+", txt))
    M = "\n".join(manifests)
    def seg(p, names):           # path has a directory segment in `names`
        parts = p.split("/")
        return any(n in parts[:-1] for n in names)
    def dep_in(subs, hay): return int(any(s in hay for s in subs))
    a = {}
    a["has_ci"]      = int(any(p.startswith(".github/workflows/") for p in paths)
                          or any(".gitlab-ci" in p or "azure-pipelines" in p for p in paths))
    a["has_tests"]   = int(any(seg(p, ("tests", "test", "spec", "__tests__")) for p in paths)
                          or any("_test." in p or ".test." in p or ".spec." in p for p in paths))
    a["has_docker"]  = int(any(os.path.basename(p).startswith("dockerfile") or "docker-compose" in p for p in paths))
    a["has_docs"]    = int(any(seg(p, ("docs", "doc")) for p in paths)
                          or any(os.path.basename(p) in ("mkdocs.yml", "book.toml") for p in paths))
    a["has_audit"]   = int(any("audit" in p or os.path.basename(p) == "security.md" for p in paths)
                          or any(s in M for s in ("certik", "trailofbits", "trail-of-bits", "slither", "mythril")))
    a["has_lintfmt"] = int(any(os.path.basename(p) in ("rustfmt.toml", "clippy.toml", ".editorconfig") for p in paths)
                          or any(".eslintrc" in p or ".prettierrc" in p for p in paths))
    a["onchain_runtime"] = int(any(seg(p, ("runtime",)) for p in paths)
                               and any("pallet" in p for p in paths))
    a["has_contracts"]   = int(any(p.endswith(".sol") or p.endswith(".ink") or seg(p, ("contracts",)) for p in paths))
    for k, subs in DEP_SIGNALS.items():
        flag = dep_in(subs, M)
        if not flag and k in ("contract", "frontend"):
            flag = dep_in(subs, "\n".join(paths))
        a[f"dep_{k}"] = flag
    a.update(fs)
    return a

FS_FIELDS = ["n_pallets","n_extrinsics","n_storage","n_events",
             "n_ink_msgs","n_sol_funcs","n_contracts_def","n_rpc"]
ATTR_FIELDS = ["project_id","repo_url","resolved_commit",
               "has_ci","has_tests","has_docker","has_docs","has_audit","has_lintfmt",
               "onchain_runtime","has_contracts",
               "dep_consensus","dep_crosschain","dep_zkcrypto","dep_contract","dep_frontend",
               *FS_FIELDS, "status"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measurements", default=str(HERE.parent.parent / "data/calibration/measurements_census.csv"))
    ap.add_argument("--out", default=str(HERE.parent.parent / "data/calibration/repo_attributes.csv"))
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(a.measurements, encoding="utf-8"))
            if r.get("status") == "OK" and r.get("repo_url") and r.get("resolved_commit")]
    existing = {}
    if os.path.exists(a.out):
        for r in csv.DictReader(open(a.out, encoding="utf-8")):
            existing[r["project_id"]] = r

    out = []; done = 0
    for r in rows:
        pid = r["project_id"]
        if not a.force and pid in existing and existing[pid].get("status") == "OK":
            out.append(existing[pid]); continue
        if a.max and done >= a.max:
            if pid in existing: out.append(existing[pid])
            continue
        rec = {f: "" for f in ATTR_FIELDS}
        rec.update(project_id=pid, repo_url=r["repo_url"], resolved_commit=r["resolved_commit"])
        try:
            d = ensure_clone(pid, r["repo_url"]); checkout(d, r["resolved_commit"])
            rec.update(probe(d)); rec["status"] = "OK"
            print(f"  probed {pid}: CI={rec['has_ci']} tests={rec['has_tests']} audit={rec['has_audit']} "
                  f"onchain={rec['onchain_runtime']} consensus={rec['dep_consensus']} zk={rec['dep_zkcrypto']} "
                  f"xchain={rec['dep_crosschain']} contract={rec['dep_contract']}")
            done += 1
        except Exception as e:
            rec["status"] = "ERROR"; print(f"  ERROR {pid}: {str(e)[:120]}")
        out.append(rec)

    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ATTR_FIELDS); w.writeheader(); w.writerows(out)
    ok = sum(1 for r in out if r.get("status") == "OK")
    print(f"Wrote {a.out}: {ok}/{len(out)} probed OK (this run measured {done})")

if __name__ == "__main__":
    main()
