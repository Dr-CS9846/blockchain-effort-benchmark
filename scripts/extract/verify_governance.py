#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_governance.py — source-verify each remaining 209 governance singleton by pulling the proposal
content from the Subsquare API and extracting the proposer-stated hours, so the figure is read from source
(not the sheet). Outputs data/calibration/governance_verified.csv for human fold-in. stdlib + urllib. CI."""
import csv, json, re, urllib.request, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/calibration/governance_verified.csv"

# (key, net, api_path, claimed_hours, claimed_name)
C = [
 ("subsquare-1225","polkadot","gov2/referendums/1225",3760,"Subsquare 12-mo maintenance+features"),
 ("orml-459","polkadot","gov2/referendums/459",3200,"ORML/Chopsticks/Subway tooling"),
 ("integritee-426","polkadot","gov2/referendums/426",926,"Integritee Private Transfers"),
 ("sdkassets-1657","polkadot","gov2/referendums/1657",196,"Polkadot SDK Assets tip"),
 ("subscan-1366","polkadot","gov2/referendums/1366",466,"Subscan Q3/Q4 2024 feature dev"),
 ("sqd-1730","polkadot","gov2/referendums/1730",480,"SQD/Subsquid indexing"),
 ("polkagate-1489","polkadot","gov2/referendums/1489",320,"PolkaGate MetaMask Snap"),
 ("subwallet-1745","polkadot","gov2/referendums/1745",1664,"SubWallet development"),
 ("polkadotcloud-1706","polkadot","gov2/referendums/1706",498,"Polkadot Cloud website (Flez)"),
 ("rfcbot-504","polkadot","gov2/referendums/504",32,"RFCs Referenda Bot"),
 ("radiumblock-544","polkadot","gov2/referendums/544",480,"RadiumBlock RPC infra"),
 ("ecosystem-1352","polkadot","gov2/referendums/1352",450,"Ecosystem Activities (BD/events)"),
 ("polkabiz-1686","polkadot","gov2/referendums/1686",None,"PolkaBiz BD"),
 ("subsquareinfra-1688","polkadot","gov2/referendums/1688",240,"Subsquare infra work"),
 ("just-spend198","polkadot","treasury/spends/198",160,"JUST/Subsquare dev (spend 198)"),
 ("justventures-spend119","polkadot","treasury/spends/119",640,"Just Ventures JUST 2.0 (spend 119)"),
 ("jam-3296","polkadot","polkassembly/posts/3296",250,"JAM Knowledge-Base Search (FluffyLabs)"),
 ("radium-khala93","khala","treasury/proposals/93",30,"RadiumBlock Khala snapshot"),
]
HOURS_RATE=re.compile(r"(\d[\d,\.]{0,5})\s*h(?:ours?)?\s*[x*×@]\s*\d",re.I)
HOURS=re.compile(r"(\d[\d,\.]{0,5})\s*(?:h\b|hours?\b|hrs?\b)",re.I)
RETRO=re.compile(r"retroactiv",re.I); DONE=re.compile(r"deliver|complet|finish|final report|maintenance|q[1-4]\s*20",re.I)
def num(s):
    try: return float(str(s).replace(",",""))
    except: return None
def hours_of(t):
    vals=[num(m.group(1)) for m in HOURS_RATE.finditer(t)] or [num(m.group(1)) for m in HOURS.finditer(t)]
    return [v for v in vals if v and 1<=v<=200000]
def fetch(net,path):
    url="https://%s-api.subsquare.io/%s"%(net,path)
    req=urllib.request.Request(url,headers={"User-Agent":"research"})
    with urllib.request.urlopen(req,timeout=40) as r: return json.loads(r.read().decode("utf-8","ignore"))
def main():
    rows=[]
    for key,net,path,claim,name in C:
        content=""; ok="ok"
        try:
            j=fetch(net,path); content=j.get("content") or (j.get("onchainData",{}) or {}).get("description","") or ""
        except Exception as e: ok="fetch_fail:%s"%str(e)[:30]
        hv=hours_of(content); tot=sum(hv) if hv else ""
        big=max(hv) if hv else ""
        rows.append(dict(key=key,name=name,claimed=claim,
            extracted_sum=(int(tot) if tot else ""), extracted_max=(int(big) if big else ""),
            n_hour_tokens=len(hv), retro=("Y" if RETRO.search(content) else ""),
            done=("Y" if DONE.search(content) else ""), status=ok,
            url="https://%s.subsquare.io/%s"%(net,path.replace("gov2/referendums","referenda")),
            snippet=";".join(str(int(x)) for x in hv[:10])))
        time.sleep(0.5)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    cols=["key","name","claimed","extracted_sum","extracted_max","n_hour_tokens","retro","done","status","url","snippet"]
    with open(OUT,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
    print("=== governance verification ===")
    for r in rows: print("  %-32s claim=%s extracted_sum=%s max=%s retro=%s done=%s [%s]"%(r["name"][:32],r["claimed"],r["extracted_sum"],r["extracted_max"],r["retro"],r["done"],r["status"]))
    print("wrote",OUT)
if __name__=="__main__": main()
