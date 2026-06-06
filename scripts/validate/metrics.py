#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metrics.py  —  the canonical accuracy-metric suite for effort estimation.

Reports MMRE alone is not enough: MMRE is provably biased toward models that
underestimate (Shepperd & MacDonell 2012; Port & Korte 2008; Foss et al. 2003),
so a credible study must also report unbiased measures. This module provides:

  MMRE, MdMRE          - mean / median magnitude of relative error (legacy, biased)
  PRED(0.25), PRED(0.30) - fraction of estimates within 25% / 30%
  MAE  (a.k.a. MAR)    - mean absolute error (unbiased)
  MARP0               - expected MAE of random guessing (all-pairs |y_i - y_j|)
  SA                  - Standardized Accuracy = 1 - MAE/MARP0  (Shepperd & MacDonell)
                        SA>0: better than random; ~0: no better than guessing
  cliffs_delta        - non-parametric effect size between two |error| vectors

Deterministic; numpy only.
"""
import numpy as np

def mre(actual, pred):
    actual = np.asarray(actual, float); pred = np.asarray(pred, float)
    return np.abs(actual - pred) / actual

def mae(actual, pred):
    return float(np.mean(np.abs(np.asarray(actual, float) - np.asarray(pred, float))))

def marp0(actual):
    """Expected MAE of random guessing: mean over all ordered pairs i!=j of |y_i - y_j|."""
    y = np.asarray(actual, float); n = len(y)
    if n < 2: return float("nan")
    d = np.abs(y[:, None] - y[None, :])
    return float(d.sum() / (n * (n - 1)))   # exclude diagonal (zeros)

def standardized_accuracy(actual, pred):
    m0 = marp0(actual)
    if not np.isfinite(m0) or m0 == 0: return float("nan")
    return float(1.0 - mae(actual, pred) / m0)

def cliffs_delta(a, b):
    """Effect size: P(a>b) - P(a<b) over all pairs. a,b are |error| vectors."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    n = len(a) * len(b)
    return float((gt - lt) / n) if n else float("nan")

def summary(actual, pred):
    actual = np.asarray(actual, float); pred = np.asarray(pred, float)
    r = mre(actual, pred)
    return {
        "n": int(len(actual)),
        "MMRE": float(np.mean(r)),
        "MdMRE": float(np.median(r)),
        "PRED25": float(np.mean(r <= 0.25)),
        "PRED30": float(np.mean(r <= 0.30)),
        "MAE": mae(actual, pred),
        "MARP0_random_baseline": marp0(actual),
        "SA_vs_random": standardized_accuracy(actual, pred),
    }
