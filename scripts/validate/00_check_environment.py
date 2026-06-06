#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
00_check_environment.py  —  run this FIRST
==========================================
Zero dependencies, zero arguments. Tells you exactly what is installed, what is
missing, and the one command to fix each gap. If every line says OK, the other
scripts will run.

    python 00_check_environment.py
"""
import shutil, subprocess, sys, os

def ok(b): return "  OK  " if b else " MISS "

def ver(tool):
    try:
        out = subprocess.run([tool,"--version"], capture_output=True, text=True)
        return (out.stdout or out.stderr).splitlines()[0].strip()
    except Exception:
        return ""

print("="*64)
print("  ENVIRONMENT CHECK  —  Size/Effort measurement toolkit")
print("="*64)

# Python
pyok = sys.version_info >= (3,8)
print(f"[{ok(pyok)}] Python {sys.version.split()[0]}  (need >= 3.8)")

# git
g = shutil.which("git"); print(f"[{ok(bool(g))}] git           {ver('git') if g else '-- install: https://git-scm.com'}")

# cloc
c = shutil.which("cloc"); print(f"[{ok(bool(c))}] cloc          {ver('cloc') if c else '-- install: apt install cloc | brew install cloc | choco install cloc'}")

# numpy
try:
    import numpy as _np; npok=True; npv=_np.__version__
except Exception:
    npok=False; npv=""
print(f"[{ok(npok)}] numpy         {npv if npok else '-- install: pip install numpy'}")

# manifest present + repo_url filled? (layered path, with flat fallback)
man = "data/calibration/projects_manifest.csv"
if not os.path.exists(man) and os.path.exists("projects_manifest.csv"):
    man = "projects_manifest.csv"
if os.path.exists(man):
    import csv
    rows=list(csv.DictReader(open(man)))
    filled=sum(1 for r in rows if r.get("repo_url","").strip())
    print(f"[{ok(True)}] manifest      {len(rows)} rows, {filled} have repo_url")
    if filled==0:
        print("        -> next: run resolve_repos.py, then fill repo_url + commit_sha/cutoff_date")
else:
    print(f"[{ok(False)}] manifest      projects_manifest.csv NOT found (looked in data/calibration/)")

print("-"*64)
allgood = pyok and g and c and npok
print("  RESULT:", "ALL GOOD — you can run measure_repos.py" if allgood
      else "Fix the MISS lines above, then re-run this check.")
print("="*64)
sys.exit(0 if allgood else 1)
