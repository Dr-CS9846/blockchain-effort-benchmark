#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_60.py - deep verification of a friend-supplied 60-point candidate list.
For each entry: (1) does the file exist at the given repo path; (2) is it RETROACTIVE
(an actual delivered hours report) or PLANNED (a grant application estimate); (3) the
reported-hours signal found in the file vs the claimed hours; (4) PM recomputed at our
152 h/PM vs the claimed PM (list uses 160 h/PM); (5) overlap with VERIFIED_PILOTS.
Clones polkascan/social-contract + w3f/Grants-Program. stdlib only. CI."""
import csv, json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOTS = ROOT / "data/calibration/VERIFIED_PILOTS.md"
OUT = ROOT / "data/calibration/verify_60.csv"
WORK = Path("/tmp/v60"); WORK.mkdir(parents=True, exist_ok=True)
DATA = json.loads(r'''[{"n": 1, "grade": "A", "name": "Polkascan DOT Prop 008  Oct 2020", "hclaim": 142.0, "pm": 0.89, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202010.md"}, {"n": 2, "grade": "A", "name": "Polkascan DOT Prop 008  Nov 2020", "hclaim": 136.0, "pm": 0.85, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202011.md"}, {"n": 3, "grade": "A", "name": "Polkascan DOT Prop 008  Dec 2020", "hclaim": 138.0, "pm": 0.86, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202012.md"}, {"n": 4, "grade": "A", "name": "Polkascan DOT Prop 008  Jan 2021", "hclaim": 139.0, "pm": 0.87, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202101.md"}, {"n": 5, "grade": "A", "name": "Polkascan DOT Prop 008  Feb 2021", "hclaim": 130.0, "pm": 0.81, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202102.md"}, {"n": 6, "grade": "A", "name": "Polkascan DOT Prop 008  Mar 2021", "hclaim": 140.0, "pm": 0.88, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202103.md"}, {"n": 7, "grade": "A", "name": "Polkascan DOT Prop 008  Apr 2021", "hclaim": 128.0, "pm": 0.8, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202104.md"}, {"n": 8, "grade": "A", "name": "Polkascan DOT Prop 008  May 2021", "hclaim": 132.0, "pm": 0.83, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202105.md"}, {"n": 9, "grade": "A", "name": "Polkascan DOT Prop 008  Jun 2021", "hclaim": 141.0, "pm": 0.88, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202106.md"}, {"n": 10, "grade": "A", "name": "Polkascan DOT Prop 008  Jul 2021", "hclaim": 162.0, "pm": 1.01, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202107.md"}, {"n": 11, "grade": "A", "name": "Polkascan DOT Prop 008  Aug 2021", "hclaim": 136.0, "pm": 0.85, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202108.md"}, {"n": 12, "grade": "A", "name": "Polkascan DOT Prop 008  Sep 2021", "hclaim": 139.0, "pm": 0.87, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-202109.md"}, {"n": 13, "grade": "A", "name": "Polkascan DOT Prop 008  Q4 2021", "hclaim": 382.0, "pm": 2.39, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2021Q4.md"}, {"n": 14, "grade": "A", "name": "Polkascan DOT Prop 008  Q1 2022", "hclaim": 92.0, "pm": 0.58, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2022Q1.md"}, {"n": 15, "grade": "A", "name": "Polkascan DOT Prop 008  Q2 2022", "hclaim": 59.0, "pm": 0.37, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2022Q2.md"}, {"n": 16, "grade": "A", "name": "Polkascan DOT Prop 008  Q3 2022", "hclaim": 91.0, "pm": 0.57, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2022Q3.md"}, {"n": 17, "grade": "A", "name": "Polkascan DOT Prop 008  Q4 2022", "hclaim": 174.0, "pm": 1.09, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2022Q4.md"}, {"n": 18, "grade": "A", "name": "Polkascan DOT Prop 008  Q1 2023", "hclaim": 202.0, "pm": 1.26, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2023Q1.md"}, {"n": 19, "grade": "A", "name": "Polkascan DOT Prop 008  Q2Q3 2023", "hclaim": 164.0, "pm": 1.03, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2023Q2-Q3.md"}, {"n": 20, "grade": "A", "name": "Polkascan DOT Prop 008  Q4 2023", "hclaim": 127.0, "pm": 0.79, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2023Q4.md"}, {"n": 21, "grade": "A", "name": "Polkascan DOT Prop 008  Q1 2024", "hclaim": 65.0, "pm": 0.41, "repo": "polkascan/social-contract", "path": "polkadot/treasury-proposal-008-report-2024Q1.md"}, {"n": 22, "grade": "A", "name": "Kusama Prop 57  Report 1 (2021-01-11)", "hclaim": 139.0, "pm": 0.87, "repo": "polkascan/social-contract", "path": "kusama/treasury-proposal-57-report-20210111.md"}, {"n": 23, "grade": "A", "name": "Kusama Prop 57  Report 2 (2021-02-16)", "hclaim": 250.0, "pm": 1.56, "repo": "polkascan/social-contract", "path": "kusama/treasury-proposal-57-report-20210216.md"}, {"n": 24, "grade": "A", "name": "Kusama Prop 164  Report (2022-09-12)", "hclaim": 346.0, "pm": 2.16, "repo": "polkascan/social-contract", "path": "kusama/treasury-proposal-164-report-20220912.md"}, {"n": 25, "grade": "A", "name": "Kusama Prop 173  Report (2022-09-12)", "hclaim": 240.0, "pm": 1.5, "repo": "polkascan/social-contract", "path": "kusama/treasury-proposal-173-report-20220912.md"}, {"n": 26, "grade": "A", "name": "Kusama Prop 214  Report (2023-01-10)", "hclaim": 326.0, "pm": 2.04, "repo": "polkascan/social-contract", "path": "kusama/treasury-proposal-214-report-20230110.md"}, {"n": 27, "grade": "A", "name": "Kusama Ref 83  Report (2023-07-18)", "hclaim": 428.0, "pm": 2.68, "repo": "polkascan/social-contract", "path": "kusama/referendum-83-report-20230718.md"}, {"n": 28, "grade": "B", "name": "W3F ink-analyzer Phase 1  M1 (Semantic Analyzer: Diagnostics)", "hclaim": 480.0, "pm": 0.75, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer.md"}, {"n": 29, "grade": "B", "name": "W3F ink-analyzer Phase 1  M2 (Code completion & hover)", "hclaim": 880.0, "pm": 1.38, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer.md"}, {"n": 30, "grade": "B", "name": "W3F ink-analyzer Phase 1  M3 (Language Server)", "hclaim": 560.0, "pm": 0.88, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer.md"}, {"n": 31, "grade": "B", "name": "W3F ink-analyzer Phase 1  M4 (VS Code Extension)", "hclaim": 560.0, "pm": 0.88, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer.md"}, {"n": 32, "grade": "B", "name": "W3F ink-analyzer Phase 2  M1", "hclaim": 880.0, "pm": 1.38, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer-phase-2.md"}, {"n": 33, "grade": "B", "name": "W3F ink-analyzer Phase 2  M2", "hclaim": 560.0, "pm": 0.88, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer-phase-2.md"}, {"n": 34, "grade": "B", "name": "W3F ink-analyzer Phase 2  M3", "hclaim": 880.0, "pm": 1.38, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer-phase-2.md"}, {"n": 35, "grade": "B", "name": "W3F ink-analyzer Phase 2  M4", "hclaim": 880.0, "pm": 1.38, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer-phase-2.md"}, {"n": 36, "grade": "B", "name": "W3F ink-analyzer Phase 2  M5", "hclaim": 560.0, "pm": 0.88, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer-phase-2.md"}, {"n": 37, "grade": "B", "name": "W3F ink-analyzer Phase 2  M6", "hclaim": 560.0, "pm": 0.88, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer-phase-2.md"}, {"n": 38, "grade": "B", "name": "W3F ink-analyzer Phase 2  M7", "hclaim": 560.0, "pm": 0.88, "repo": "w3f/Grants-Program", "path": "applications/ink-analyzer-phase-2.md"}, {"n": 39, "grade": "B", "name": "W3F DOT Login  M1", "hclaim": 2880.0, "pm": 18, "repo": "w3f/Grants-Program", "path": "applications/dot-login.md"}, {"n": 40, "grade": "B", "name": "W3F DOT Login  M2", "hclaim": 320.0, "pm": 2, "repo": "w3f/Grants-Program", "path": "applications/dot-login.md"}, {"n": 41, "grade": "B", "name": "W3F Afloat  M1", "hclaim": 640.0, "pm": 2.5, "repo": "w3f/Grants-Program", "path": "applications/Afloat.md"}, {"n": 42, "grade": "B", "name": "W3F Afloat  M2", "hclaim": 512.0, "pm": 2, "repo": "w3f/Grants-Program", "path": "applications/Afloat.md"}, {"n": 43, "grade": "B", "name": "W3F Afloat  M3", "hclaim": 256.0, "pm": 0.5, "repo": "w3f/Grants-Program", "path": "applications/Afloat.md"}, {"n": 44, "grade": "B", "name": "W3F Afloat  M4", "hclaim": 256.0, "pm": 0.5, "repo": "w3f/Grants-Program", "path": "applications/Afloat.md"}, {"n": 45, "grade": "B", "name": "W3F Aisland-DocSig  M1", "hclaim": 240.0, "pm": 1.5, "repo": "w3f/Grants-Program", "path": "applications/Aisland-DocSig.md"}, {"n": 46, "grade": "B", "name": "W3F Aisland-DocSig  M2", "hclaim": 240.0, "pm": 1.5, "repo": "w3f/Grants-Program", "path": "applications/Aisland-DocSig.md"}, {"n": 47, "grade": "B", "name": "W3F AlgoCash  M1", "hclaim": 560.0, "pm": 3.5, "repo": "w3f/Grants-Program", "path": "applications/AlgoCash.md"}, {"n": 48, "grade": "B", "name": "W3F ArtZero InkWhale  M1", "hclaim": 800.0, "pm": 5, "repo": "w3f/Grants-Program", "path": "applications/ArtZero_InkWhale.md"}, {"n": 49, "grade": "B", "name": "W3F ArtZero InkWhale  M2", "hclaim": 800.0, "pm": 5, "repo": "w3f/Grants-Program", "path": "applications/ArtZero_InkWhale.md"}, {"n": 50, "grade": "B", "name": "W3F AdMeta  M1", "hclaim": 1920.0, "pm": 12, "repo": "w3f/Grants-Program", "path": "applications/AdMeta.md"}, {"n": 51, "grade": "B", "name": "W3F Yatima  M1", "hclaim": 240.0, "pm": 1.5, "repo": "w3f/Grants-Program", "path": "applications/yatima.md"}, {"n": 52, "grade": "B", "name": "W3F Yatima  M2", "hclaim": 240.0, "pm": 1.5, "repo": "w3f/Grants-Program", "path": "applications/yatima.md"}, {"n": 53, "grade": "B", "name": "W3F Yatima  M3", "hclaim": 480.0, "pm": 3, "repo": "w3f/Grants-Program", "path": "applications/yatima.md"}, {"n": 54, "grade": "B", "name": "W3F Zenlink DEX  M1", "hclaim": 320.0, "pm": 2, "repo": "w3f/Grants-Program", "path": "applications/zenlink.md"}, {"n": 55, "grade": "B", "name": "W3F ZK Rollups on Polkadot  M1", "hclaim": 120.0, "pm": 0.75, "repo": "w3f/Grants-Program", "path": "applications/zk-rollups.md"}, {"n": 56, "grade": "B", "name": "W3F zkwasm Rollups Transfer  M1 (Crypto Primitive)", "hclaim": 640.0, "pm": 4, "repo": "w3f/Grants-Program", "path": "applications/zkwasm-rollups-transfer.md"}, {"n": 57, "grade": "B", "name": "W3F zkwasm Rollups Transfer  M2 (Nova Folding Snarks)", "hclaim": 960.0, "pm": 6, "repo": "w3f/Grants-Program", "path": "applications/zkwasm-rollups-transfer.md"}, {"n": 58, "grade": "B", "name": "W3F YieldScan Phase 2  M1", "hclaim": 720.0, "pm": 4.5, "repo": "w3f/Grants-Program", "path": "applications/yieldscan_phase_2.md"}, {"n": 59, "grade": "B", "name": "W3F DOT Login  M2", "hclaim": 320.0, "pm": 2, "repo": "w3f/Grants-Program", "path": "applications/dot-login.md"}, {"n": 60, "grade": "B", "name": "W3F DOT Login  M3", "hclaim": 240.0, "pm": 1.5, "repo": "w3f/Grants-Program", "path": "applications/dot-login.md"}]''')
REPOS = {"polkascan/social-contract": "https://github.com/polkascan/social-contract.git",
         "w3f/Grants-Program": "https://github.com/w3f/Grants-Program.git"}

def clone(url, dest):
    if not dest.exists():
        subprocess.run(["git","clone","--depth","1",url,str(dest)],
                       capture_output=True, text=True)

def pilot_index():
    """name tokens + repo basenames already in our set."""
    txt = PILOTS.read_text(encoding="utf-8")
    repos = set(m.lower() for m in re.findall(r"[A-Za-z0-9_.-]+/([A-Za-z0-9_.-]+)", txt))
    names = txt.lower()
    return repos, names

def hour_signals(text):
    # capture integers near 'h'/'hour' and any 'total ... NN'
    nums = re.findall(r"(\d[\d,]{1,6})\s*(?:h\b|hours?\b|hrs?\b)", text, re.I)
    nums = [int(x.replace(",","")) for x in nums]
    return sorted(set(nums))

def main():
    for repo,url in REPOS.items():
        clone(url, WORK / repo.split("/")[1])
    prepos, pnames = pilot_index()
    rows=[]
    for e in DATA:
        repo_dir = WORK / e["repo"].split("/")[1]
        fp = repo_dir / e["path"]
        exists = fp.exists()
        text = fp.read_text(encoding="utf-8", errors="ignore") if exists else ""
        grade = e["grade"]
        retro = "Y" if grade=="A" else "N"   # A=delivered report, B=application estimate
        # content retro double-check for A: a real report mentions hours + a period
        if grade=="A" and exists and not re.search(r"hour|\bh\b|spent|report", text, re.I):
            retro = "Y?"
        hsig = hour_signals(text) if exists else []
        hclaim = e["hclaim"]
        claim_seen = ("Y" if (hclaim and int(hclaim) in hsig) else "")
        our_pm = round(hclaim/152.0, 2) if hclaim else ""
        pm_claim = e["pm"]
        pm_match = ""
        if our_pm!="" and pm_claim:
            pm_match = "same@152" if abs(our_pm-pm_claim)<=0.03 else "DIFFERS(conv 160 vs 152)"
        # overlap with our list
        key = re.split(r"[ \-]", e["name"])
        inlist=""
        for tok in ["ink-analyzer","AlgoCash","ArtZero","Afloat","zenlink","yieldscan",
                    "Aisland","dot-login","AdMeta","yatima","zkwasm","zk-rollup","Polkascan"]:
            if tok.lower() in e["name"].lower():
                base=tok.lower().replace("-","").replace("_","")
                hit = any(base in r.replace("-","").replace("_","") for r in prepos) or (tok.lower() in pnames)
                inlist = ("YES:"+tok) if hit else ("no")
                break
        rows.append(dict(n=e["n"], grade=grade, name=e["name"][:46], exists=("Y" if exists else "MISSING"),
                         retroactive=retro, hclaim=(int(hclaim) if hclaim else ""), pm_claim=pm_claim,
                         our_pm_152=our_pm, pm_check=pm_match, claim_in_file=claim_seen,
                         hours_found=";".join(map(str,hsig[:8])), in_our_list=inlist))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols=["n","grade","name","exists","retroactive","hclaim","pm_claim","our_pm_152","pm_check",
          "claim_in_file","hours_found","in_our_list"]
    with open(OUT,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
    miss=[r for r in rows if r["exists"]!="Y"]
    notretro=[r for r in rows if r["retroactive"].startswith("N")]
    inl=[r for r in rows if r["in_our_list"].startswith("YES")]
    print("=== verify_60: %d entries ===" % len(rows))
    print("MISSING files: %d -> %s" % (len(miss), ", ".join("#%s"%r["n"] for r in miss)))
    print("NOT retroactive (planned apps): %d -> #%s" % (len(notretro), ",".join(str(r["n"]) for r in notretro)))
    print("Overlap with our list: %d -> %s" % (len(inl), ", ".join("#%s(%s)"%(r["n"],r["in_our_list"]) for r in inl)))
    print("Grade A claim-in-file matches: %d/27" % sum(1 for r in rows if r["grade"]=="A" and r["claim_in_file"]=="Y"))
    print("wrote", OUT)

if __name__=="__main__":
    main()
