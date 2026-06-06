#!/usr/bin/env bash
# Portable one-command pipeline for environments without `make`.
# Tolerant: runs end-to-end and always regenerates the baseline + figures,
# skipping steps whose tools/data are absent (with a clear message).
set -uo pipefail
cd "$(dirname "$0")"
MANIFEST=data/calibration/projects_manifest.csv
DATASET=data/calibration/w3f_benchmark_dataset.csv
MEAS=data/calibration/measurements.csv
mkdir -p reports
echo "== setup ==";     python scripts/validate/00_check_environment.py || true
echo "== resolve ==";   python scripts/extract/resolve_repos_online.py --manifest "$MANIFEST" || echo "resolve needs network"
echo "== measure ==";   python scripts/extract/measure_repos.py --manifest "$MANIFEST" --out "$MEAS" || echo "measure needs git + cloc"
echo "== calibrate =="; python scripts/validate/calibrate_size_effort.py --csv "$MEAS" --effort measured && \
                        mv -f size_effort_params.json size_effort_results.json reports/ 2>/dev/null || echo "calibrate needs measurements"
echo "== baseline ==";  python scripts/validate/calibrate_bc_cocomo.py --csv "$DATASET" --outdir reports && \
                        mv -f reports/params.json reports/bc_cocomo_params.json && \
                        mv -f reports/results.json reports/bc_cocomo_results.json
echo "== figures ==";   python scripts/validate/make_figures.py
echo "run_all complete."
