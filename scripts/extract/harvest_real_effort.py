#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harvest_real_effort.py — discover RETROACTIVE, COMPLETED, itemised-effort reports at scale.
Two proven clean veins:
  A) gh code-search for the actual-hours reporting fingerprints -> team report repos (Polkascan/stakeworld-like),
     then clone each candidate repo and extract per-file reported hours.
  B) Subsquare/Polkassembly governance API (Polkadot+Kusama treasury proposals + OpenGov referenda): pull content,
     keep only RETROACTIVE items that carry an itemised hours table ("N h x RATE", "hours spent", "time spent",
     "person-months"), and extract the hours.
Output: data/calibration/harvested_effort.csv  (vein, source, title/proposer, retroactive, hours, pm_152, url, snippet).
Everything here is a CANDIDATE for human verification — nothing is admitted automatically. stdlib + git + gh + curl(API only). CI."""
import csv, json, os, re, subprocess, glob, urllib.request, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/calibration/harvested_effort.csv"
WORK = Path("/tmp/harvest"); WORK.mkdir(parents=True, exist_ok=True)

HOURS_RATE = re.compile(r"(\d[\d,\.]{0,5})\s*h(?:ours?)?\s*[x*×]\s*\d", re.I)          # "12 h x 85 EUR"
HOURS_SPENT = re.compile(r"(\d[\d,\.]{0,5})\s*(?:h\b|hours?\b|hrs?\b)\s*(?:spent|of work|logged)?", re.I)
TIME_SPENT = re.compile(r"(?:time spent|hours spent|total .*hours)\D{0,12}(\d[\d,\.]{0,5})", re.I)
PM_RE = re.compile(r"(\d[\d,\.]{0,4})\s*(?:person[\s-]?months?|man[\s-]?months?)", re.I)
RETRO = re.compile(r"\bretroactiv", re.I)
DONE = re.compile(r"\b(deliver(ed|y)|completed|final report|finished|done|maintenance for|in Q[1-4])\b", re.I)

def num(s):
    try: return float(str(s).replace(",", ""))
    except Exception: return None

def all_hours(txt):
    vals = []
    for rx in (HOURS_RATE, TIME_SPENT, HOURS_SPENT):
        for m in rx.finditer(txt):
            v = num(m.group(1))
            if v and 1 <= v <= 100000: vals.append(v)
    return vals

def pm_vals(txt):
    return [num(m.group(1)) for m in PM_RE.finditer(txt) if num(m.group(1))]

# ---------- vein A: gh code-search -> repos -> clone -> extract ----------
FINGERPRINTS = [
    '"Total Development Hours Spent"',
    '"time spent per category"',
    '"hours spent" "Feature development"',
    '"h x 85 EUR" OR "h x 80 EUR" treasury',
    '"hours" "EUR/hour" treasury proposal',
    '"person-months" delivered grant substrate',
]
REPO_OK = re.compile(r"polkadot|kusama|substrate|web3|treasury|grant|\bink\b|dotsama|parachain|stakeworld|polkascan", re.I)
def gh_repos():
    repos = set()
    for q in FINGERPRINTS:
        try:
            r = subprocess.run(["gh","search","code",q,"-L","60","--json","repository"],
                               capture_output=True, text=True, timeout=60)
            for it in json.loads(r.stdout or "[]"):
                nm = it["repository"]["nameWithOwner"]
                if REPO_OK.search(nm):              # drop unrelated student/personal projects
                    repos.add(nm)
        except Exception as e:
            print("  gh search failed:", q, e)
        time.sleep(2)
    return sorted(repos)

def harvest_repo(nameWithOwner, rows):
    d = WORK / nameWithOwner.replace("/","__")
    if not d.exists():
        subprocess.run(["git","clone","--depth","1",f"https://github.com/{nameWithOwner}.git",str(d)],
                       capture_output=True, text=True, timeout=120)
    for p in glob.glob(str(d/"**"/"*.md"), recursive=True):
        name = os.path.basename(p)
        if name.lower() in ("readme.md",): continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        hv = all_hours(txt); pv = pm_vals(txt)
        if not hv and not pv: continue
        retro = "Y" if RETRO.search(txt) else ""
        done = "Y" if DONE.search(txt) else ""
        tot = sum(hv) if hv else (pv[0]*152 if pv else 0)
        rows.append(dict(vein="repo", source=nameWithOwner, title=name, proposer="",
                         retroactive=retro, completed=done, hours=(int(tot) if hv else ""),
                         pm_152=(round(tot/152.0,2) if tot else ""),
                         url=f"https://github.com/{nameWithOwner}/blob/master/{name}",
                         snippet=(("hours="+",".join(map(str,map(int,hv[:6])))) if hv else ("pm="+str(pv[:3])))[:90]))

# ---------- vein B: Subsquare governance API ----------
APIS = {
  "polkadot-treasury":"https://polkadot-api.subsquare.io/treasury/proposals?page=%d&pageSize=50",
  "kusama-treasury":"https://kusama-api.subsquare.io/treasury/proposals?page=%d&pageSize=50",
  "polkadot-ref":"https://polkadot-api.subsquare.io/gov2/referendums?page=%d&pageSize=50",
  "kusama-ref":"https://kusama-api.subsquare.io/gov2/referendums?page=%d&pageSize=50",
}
def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent":"research-harvester"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8","ignore"))

DETAIL = {
  "polkadot-treasury":"https://polkadot-api.subsquare.io/treasury/proposals/%s",
  "kusama-treasury":"https://kusama-api.subsquare.io/treasury/proposals/%s",
  "polkadot-ref":"https://polkadot-api.subsquare.io/gov2/referendums/%s",
  "kusama-ref":"https://kusama-api.subsquare.io/gov2/referendums/%s",
}
def harvest_subsquare(rows):
    for net, tmpl in APIS.items():
        pages = 40 if net.endswith("ref") else 16    # cover ~2000 referenda / ~800 treasury proposals
        for page in range(1, pages+1):
            try: j = fetch_json(tmpl % page)
            except Exception as e:
                print("  api fail", net, page, e); break
            items = j.get("items", j if isinstance(j,list) else [])
            if not items: break
            for it in items:
                title = (it.get("title") or "")
                listcontent = (it.get("content") or "")
                if not RETRO.search(title + "\n" + listcontent):   # CLEAN: retroactive only
                    continue
                idx = it.get("referendumIndex", it.get("proposalIndex", it.get("_id","")))
                # detail-fetch FULL content (list endpoint truncates the hour tables)
                content = listcontent
                try:
                    dj = fetch_json(DETAIL[net] % idx); content = dj.get("content") or listcontent
                except Exception: pass
                time.sleep(0.3)
                hv = all_hours(content); pv = pm_vals(content)
                if not hv and not pv: continue
                tot = sum(hv) if hv else (pv[0]*152 if pv else 0)
                base = "https://%s.subsquare.io" % net.split("-")[0]
                path = ("/referenda/%s" % idx) if "ref" in net else ("/treasury/proposals/%s" % idx)
                rows.append(dict(vein=net, source="subsquare", title=title[:80],
                                 proposer=(it.get("proposer") or "")[:24], retroactive="Y",
                                 completed=("Y" if DONE.search(title+content) else ""),
                                 hours=(int(tot) if hv else ""), pm_152=(round(tot/152.0,2) if tot else ""),
                                 url=base+path, snippet=(("hours="+",".join(map(str,map(int,hv[:8])))) if hv else ("pm="+str(pv[:3])))[:90]))
            time.sleep(0.3)

def main():
    rows=[]
    print("=== vein A: gh code-search repos ===")
    repos = gh_repos(); print("candidate repos:", repos)
    for r in repos: harvest_repo(r, rows)
    print("=== vein B: subsquare governance ===")
    harvest_subsquare(rows)
    # dedupe by (source,title)
    seen=set(); ded=[]
    for r in rows:
        k=(r["source"],r["title"])
        if k in seen: continue
        seen.add(k); ded.append(r)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols=["vein","source","title","proposer","retroactive","completed","hours","pm_152","url","snippet"]
    with open(OUT,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(ded)
    retro=[r for r in ded if r["retroactive"]=="Y"]
    print("=== harvested %d candidates (%d retroactive) ===" % (len(ded), len(retro)))
    print("by vein:", {v:sum(1 for r in ded if r['vein']==v) for v in set(r['vein'] for r in ded)})
    for r in ded[:60]:
        print("  [%s] %s | retro=%s done=%s h=%s pm=%s | %s" % (r['vein'][:10], r['title'][:40], r['retroactive'], r['completed'], r['hours'], r['pm_152'], r['url']))
    print("wrote", OUT)

if __name__=="__main__":
    main()
