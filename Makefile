# One-command reproducible pipeline (Phase 2). Uses .RECIPEPREFIX so recipes
# are prefixed with '>' instead of a literal tab (portable across editors).
.RECIPEPREFIX = >
.PHONY: help setup baseline resolve measure calibrate figures quickcheck all verify clean

MANIFEST = data/calibration/projects_manifest.csv
DATASET  = data/calibration/w3f_benchmark_dataset.csv
MEAS     = data/calibration/measurements.csv

help:
> @echo "Targets:"
> @echo "  make setup      - check tools (git, cloc, numpy)"
> @echo "  make baseline   - reproduce the honest BC-COCOMO baseline (no cloc/git needed)"
> @echo "  make figures    - regenerate figures from locked results"
> @echo "  make quickcheck - setup + baseline + figures (reproducible subset; no cloc/git)"
> @echo "  make resolve    - resolve delivered repos + commits (needs network)"
> @echo "  make measure    - clone + cloc + git-effort -> measurements.csv (needs git, cloc)"
> @echo "  make calibrate  - fit size->effort on measurements (needs numpy)"
> @echo "  make all        - full pipeline: setup resolve measure calibrate figures"
> @echo "  make verify     - re-run baseline; confirm it matches committed results"
> @echo "  make clean      - remove regenerable intermediates (keeps evidence)"

setup:
> @python scripts/validate/00_check_environment.py || true

baseline:
> python scripts/validate/calibrate_bc_cocomo.py --csv $(DATASET) --outdir reports
> mv -f reports/params.json reports/bc_cocomo_params.json
> mv -f reports/results.json reports/bc_cocomo_results.json
> @echo "baseline reproduced -> reports/bc_cocomo_results.json"

resolve:
> python scripts/extract/resolve_repos_online.py --manifest $(MANIFEST)

measure:
> python scripts/extract/measure_repos.py --manifest $(MANIFEST) --out $(MEAS)

calibrate:
> python scripts/validate/calibrate_size_effort.py --csv $(MEAS) --effort measured
> python scripts/validate/calibrate_size_effort.py --csv $(MEAS) --effort planned || true
> mkdir -p reports
> mv -f size_effort_params.json size_effort_results.json reports/ 2>/dev/null || true

figures:
> python scripts/validate/make_figures.py

quickcheck: setup baseline figures
> @echo "quickcheck complete (reproducible subset; needs no cloc/git)."

all: setup freeze resolve measure calibrate figures
> @echo "full pipeline complete."

verify:
> python scripts/validate/calibrate_bc_cocomo.py --csv $(DATASET) --outdir reports/.verify
> python -c "import json;a=json.load(open('reports/bc_cocomo_results.json'))['loocv'];b=json.load(open('reports/.verify/results.json'))['loocv'];m=abs(a['MMRE']-b['MMRE'])<1e-9 and abs(a['PRED25']-b['PRED25'])<1e-9;print('VERIFY:',('MATCH' if m else 'MISMATCH'),'MMRE=%.4f PRED25=%.4f'%(b['MMRE'],b['PRED25']))"

clean:
> rm -rf repo_cache __pycache__ reports/.verify 2>/dev/null || true
> @echo "cleaned intermediates."

freeze:
> python scripts/extract/freeze_raw.py --manifest $(MANIFEST)
