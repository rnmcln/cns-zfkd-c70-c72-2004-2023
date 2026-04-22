#!/usr/bin/env bash
# Full reproducibility pipeline: raw ZfKD CSVs -> tidy tables -> analyses -> tables & figures.
# Prerequisite: `pip install -r requirements.txt` in a Python 3.11 env.
set -euo pipefail
cd "$(dirname "$0")"

echo "[1/5] Parsing raw CSV exports to tidy long-format..."
python -m src.parse_csv

echo "[2/5] Running trend analyses (APC, OLS, HAC(1), MK, Theil-Sen, MIR)..."
python -m src.run_analysis

echo "[3/5] Generating tables..."
python -m src.make_tables

echo "[4/5] Generating figures..."
python -m src.make_figures

echo "[5/5] Running QA checks..."
python -m src.qa_checks

# Optional drift guard: only runs if the canonical tables DOCX has been regenerated
if [ -f "tables/tables_JCRCO_rev_v2.docx" ]; then
  echo "[optional] Drift guard: tables DOCX vs analysis_results.json..."
  python src/render_docx_stub.py \
    --json analysis_results.json \
    --docx tables/tables_JCRCO_rev_v2.docx
fi

echo "Done. Outputs now in ./tables, ./figures, and ./analysis_results.json."
