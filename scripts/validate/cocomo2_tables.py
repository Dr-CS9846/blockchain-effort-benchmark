#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cocomo2_tables.py  —  VERIFIED COCOMO II.2000 Post-Architecture constants & tables
==================================================================================
Single source of truth for the COCOMO II model values. EVERY number below was
verified verbatim against the official *COCOMO II Model Definition Manual,
version 2.1 (2000)*, USC Center for Software Engineering (Boehm et al.):
  - A = 2.94, B = 0.91                       (Manual §, "A 2.94 (for COCOMO II.2000)")
  - Scale Factor values                      (Manual Table 10)
  - Effort Multiplier values (17 drivers)    (Manual Tables 17-34)
Ratings order: [VL, L, N, H, VH, XH]; None = "n/a" (rating not defined for that driver).
Nominal (N) = 1.00 for every effort multiplier, and is the default when a variable
cannot be objectively synthesized.
"""

A = 2.94          # COCOMO II.2000 multiplicative constant (calibrated)
B = 0.91          # COCOMO II.2000 base scale exponent

RATINGS = ["VL", "L", "N", "H", "VH", "XH"]

# Scale factors SFj (summed: E = B + 0.01 * Σ SFj). Manual Table 10.
SCALE_FACTORS = {
    "PREC": [6.20, 4.96, 3.72, 2.48, 1.24, 0.00],
    "FLEX": [5.07, 4.05, 3.04, 2.03, 1.01, 0.00],
    "RESL": [7.07, 5.65, 4.24, 2.83, 1.41, 0.00],
    "TEAM": [5.48, 4.38, 3.29, 2.19, 1.10, 0.00],
    "PMAT": [7.80, 6.24, 4.68, 3.12, 1.56, 0.00],
}

# Effort multipliers (Post-Architecture), Manual Tables 17-34. None = n/a.
EFFORT_MULTIPLIERS = {
    # Product
    "RELY": [0.82, 0.92, 1.00, 1.10, 1.26, None],
    "DATA": [None, 0.90, 1.00, 1.14, 1.28, None],
    "CPLX": [0.73, 0.87, 1.00, 1.17, 1.34, 1.74],
    "RUSE": [None, 0.95, 1.00, 1.07, 1.15, 1.24],
    "DOCU": [0.81, 0.91, 1.00, 1.11, 1.23, None],
    # Platform
    "TIME": [None, None, 1.00, 1.11, 1.29, 1.63],
    "STOR": [None, None, 1.00, 1.05, 1.17, 1.46],
    "PVOL": [None, 0.87, 1.00, 1.15, 1.30, None],
    # Personnel
    "ACAP": [1.42, 1.19, 1.00, 0.85, 0.71, None],
    "PCAP": [1.34, 1.15, 1.00, 0.88, 0.76, None],
    "PCON": [1.29, 1.12, 1.00, 0.90, 0.81, None],
    "APEX": [1.22, 1.10, 1.00, 0.88, 0.81, None],
    "PLEX": [1.19, 1.09, 1.00, 0.91, 0.85, None],
    "LTEX": [1.20, 1.09, 1.00, 0.91, 0.84, None],
    # Project
    "TOOL": [1.17, 1.09, 1.00, 0.90, 0.78, None],
    "SITE": [1.22, 1.09, 1.00, 0.93, 0.86, 0.80],
    "SCED": [1.43, 1.14, 1.00, 1.00, 1.00, None],
}

EM_GROUPS = {
    "Product":   ["RELY", "DATA", "CPLX", "RUSE", "DOCU"],
    "Platform":  ["TIME", "STOR", "PVOL"],
    "Personnel": ["ACAP", "PCAP", "PCON", "APEX", "PLEX", "LTEX"],
    "Project":   ["TOOL", "SITE", "SCED"],
}

def sf_value(name, rating):
    return SCALE_FACTORS[name][RATINGS.index(rating)]

def em_value(name, rating):
    v = EFFORT_MULTIPLIERS[name][RATINGS.index(rating)]
    if v is None:
        raise ValueError(f"{name} has no '{rating}' rating (n/a in COCOMO II.2000)")
    return v

def exponent_E(sf_ratings):
    return B + 0.01 * sum(sf_value(sf, r) for sf, r in sf_ratings.items())

if __name__ == "__main__":
    # self-check: 22 variables present, nominal column == 1.00 for all EMs
    assert len(SCALE_FACTORS) == 5 and len(EFFORT_MULTIPLIERS) == 17
    assert all(EFFORT_MULTIPLIERS[e][RATINGS.index("N")] == 1.00 for e in EFFORT_MULTIPLIERS)
    print("COCOMO II.2000 tables OK: 5 SF + 17 EM; A=2.94 B=0.91; Nominal EM=1.00")
