#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_report_totals.py — recompute the CANONICAL total effort of every Polkascan and Stakeworld
report directly from the raw source files, so every number in the final dataset is source-backed
(not transcribed). Clones the two report repos and extracts per-file totals with an explicit method tag.
Output: data/calibration/report_totals_verified.csv. stdlib + git. CI."""
import csv, os, re, subprocess, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/calibration/report_totals_verified.csv"
WORK = Path("/tmp/verify_totals"); WORK.mkdir(parents=True, exist_ok=True)

def clone(url, dest):
    if not dest.exists():
        subprocess.run(["git","clone","--depth","1",url,str(dest)], capture_output=True, text=True)

# ---- Polkascan: monthly "time spent per category" tables, "Total Development Hours Spent: N", or "| Total | N |"
def polkascan_total(txt):
    # 1) explicit section totals (delivery reports, e.g. PolkADAPT 264 + Explorer UI 164)
    sect = [int(x) for x in re.findall(r"Total Development Hours Spent[:\s|]*?(\d{1,5})", txt, re.I)]
    if sect: return sum(sect), "sum_section_totals(%s)" % "+".join(map(str,sect))
    # 2) table 'Total' rows  | Total | 240 |
    tot = [int(x) for x in re.findall(r"\|\s*Total\s*\|\s*(\d{1,5})\s*\|", txt, re.I)]
    if tot: return sum(tot), "sum_table_totals(%s)" % "+".join(map(str,tot))
    # 3) sum the 'Hours spent' columns across all category tables (monthly reports & multi-contributor)
    #    capture data rows of a table that has a 'Hours spent' header
    vals=[]
    for block in re.split(r"\n#", txt):
        if re.search(r"hours\s*spent", block, re.I):
            # rows like: | Category name | 31 |
            for m in re.finditer(r"\|[^\n|]+\|\s*(\d{1,4})\s*\|", block):
                vals.append(int(m.group(1)))
    if vals: return sum(vals), "sum_category_rows(%d rows=%s)" % (len(vals), "+".join(map(str,vals[:12])))
    return None, "NO_HOURS_FOUND"

# ---- Stakeworld: dev/ops hours from '...h x RATE EUR' lines (exclude pure node/hosting cost lines)
def stakeworld_hours(txt):
    total=0; parts=[]
    for line in txt.splitlines():
        if not re.search(r"\d\s*h\b", line): continue
        if re.search(r"dedicated node|hosting|server rent|cloudflare", line, re.I): continue
        m = re.search(r"(\d+)\s*months?\s*x\s*(\d+)\s*h", line, re.I)     # 3 months x 12 h
        if m:
            v=int(m.group(1))*int(m.group(2)); total+=v; parts.append("%sx%s"%(m.group(1),m.group(2))); continue
        m = re.search(r"(\d+)\s*h\s*x\s*\d+\s*eur", line, re.I)            # 20 h x 85 EUR (one-time)
        if m:
            total+=int(m.group(1)); parts.append(m.group(1)); continue
    return (total, "sum_devhours(%s)"%"+".join(parts)) if total else (None,"NO_HOURS")

def main():
    clone("https://github.com/polkascan/social-contract.git", WORK/"polkascan")
    clone("https://github.com/stakeworld/stakeworld-treasury.git", WORK/"stakeworld")
    rows=[]
    for p in sorted(glob.glob(str(WORK/"polkascan"/"**"/"*report*.md"), recursive=True)):
        txt=open(p,encoding="utf-8",errors="ignore").read()
        tot,method=polkascan_total(txt)
        rows.append(dict(team="Polkascan", file=os.path.relpath(p, WORK/"polkascan"),
                         total_hours=(tot if tot else ""), pm_152=(round(tot/152.0,2) if tot else ""), method=method))
    for p in sorted(glob.glob(str(WORK/"stakeworld"/"*.md"))):
        name=os.path.basename(p)
        if name.lower() in ("readme.md",): continue
        txt=open(p,encoding="utf-8",errors="ignore").read()
        if not re.search(r"eur/hour|h x \d+ eur|hours are included", txt, re.I): continue
        tot,method=stakeworld_hours(txt)
        rows.append(dict(team="Stakeworld", file=name, total_hours=(tot if tot else ""),
                         pm_152=(round(tot/152.0,2) if tot else ""), method=method))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["team","file","total_hours","pm_152","method"]); w.writeheader(); w.writerows(rows)
    print("=== verified %d report totals ===" % len(rows))
    for r in rows: print("  %-10s %-52s %s h  [%s]" % (r["team"], r["file"][:52], r["total_hours"], r["method"][:60]))
    print("wrote", OUT)

if __name__=="__main__":
    main()
