#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_figures.py  —  regenerate the repository's figures from locked results.
Deterministic; reads JSON outputs only (never re-fits). matplotlib is optional:
if absent, the step is skipped cleanly so the pipeline never hard-fails.

Outputs (reports/figures/):
  baseline_actual_vs_pred.png  — honest BC-COCOMO baseline (LOOCV)
  size_effort_fit.png          — measured size vs effort with power-law fit (when available)
"""
import json, os, sys
OUT = "reports/figures"; os.makedirs(OUT, exist_ok=True)
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    print("matplotlib not installed - skipping figures (pip install matplotlib to enable).")
    sys.exit(0)

def load(p):
    return json.load(open(p)) if os.path.exists(p) else None

def scatter_actual_pred(actual, pred, title, path, label="project"):
    lo = min(min(actual), min(pred)) * 0.8
    hi = max(max(actual), max(pred)) * 1.2
    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    ax.plot([lo, hi], [lo, hi], "--", color="#888", lw=1, label="perfect (y = x)")
    ax.scatter(actual, pred, color="#028090", s=42, zorder=3, edgecolor="white")
    ax.set_xlabel("Actual effort (PM)"); ax.set_ylabel("Predicted effort (PM)")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_title(title, fontsize=11); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(path, dpi=150); plt.close(fig); print("wrote", path)

# 1) honest baseline (BC-COCOMO) — LOOCV actual vs predicted
b = load("reports/bc_cocomo_results.json")
if b and "actual_pm" in b and "loocv_predicted_pm" in b:
    mm = b.get("loocv", {}).get("MMRE"); pr = b.get("loocv", {}).get("PRED25")
    t = "BC-COCOMO II baseline (LOOCV)"
    if mm is not None: t += f"\nMMRE {mm*100:.1f}%, PRED(25) {pr*100:.1f}% - reproducible"
    scatter_actual_pred(b["actual_pm"], b["loocv_predicted_pm"], t,
                        f"{OUT}/baseline_actual_vs_pred.png")
else:
    print("baseline results not found - skipping baseline figure.")

# 2) size -> effort fit (only when real measurements exist)
s = load("reports/size_effort_results.json")
if s and all(k in s for k in ("size", "effort_actual", "loocv_pred")):
    import math
    size = s["size"]; eff = s["effort_actual"]; pred = s["loocv_pred"]
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    ax.scatter(size, eff, color="#16213F", s=42, zorder=3, edgecolor="white", label="measured")
    order = sorted(range(len(size)), key=lambda i: size[i])
    ax.plot([size[i] for i in order], [pred[i] for i in order], color="#028090", lw=1.5, label="PM = A*KSLOC^E (LOOCV)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Size (KSLOC, measured)"); ax.set_ylabel("Effort (active person-months)")
    ax.set_title("Measured size vs effort", fontsize=11); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(f"{OUT}/size_effort_fit.png", dpi=150); plt.close(fig)
    print("wrote", f"{OUT}/size_effort_fit.png")
else:
    print("measured size->effort results not found yet - skipping (awaits CI measurement).")
print("figures step complete.")
