# CNS tumours (ICD-10-GM C70-C72) in Germany, 2004-2023

Minimal reproducibility + context package (v2.0-rev, 2026-04-23) for:

> Lawson McLean A, Kahr J, Ernst T, Crodel C, Kamp MA, Senft C. (2026)
> Twenty Years of Central Nervous System Tumours in Germany: A Population-Based
> Descriptive Analysis of Incidence, Mortality, Survival, and Prevalence
> (2004-2023). *Journal of Cancer Research and Clinical Oncology*, submitted.

This repository ships only the files needed to (a) reproduce every
numeric claim in the paper from the raw ZfKD DatenBrowser exports and
(b) inspect the canonical numeric outputs. Derived artefacts (tidy CSVs, tables DOCX, figure PDFs/PNGs)
are **not** shipped — they are regenerated deterministically by
`bash run_all.sh`.

## Contents

```
.
├── README.md                   # this file
├── SUMMARY.md                  # project + results narrative
├── LICENSE                     # MIT (code); ZfKD terms for data
├── CITATION.cff                # citation metadata
├── .zenodo.json                # Zenodo deposition metadata
├── .gitignore                  # ignores derived outputs + caches
├── requirements.txt            # pinned Python 3.11 deps
├── run_all.sh                  # single-command pipeline
├── CHECKSUMS.txt               # SHA-256 of all raw ZfKD inputs (30 files)
├── analysis_results.json       # canonical numeric outputs (APC, HAC, DW, MK, TS)
├── src/                        # analysis code (9 modules)
│   ├── parse_csv.py
│   ├── parse_metadata.py
│   ├── run_analysis.py
│   ├── make_tables.py
│   ├── make_figures.py
│   ├── qa_checks.py
│   ├── utils.py
│   └── render_docx_stub.py     # numeric drift guard vs analysis_results.json
├── data_raw/                   # 16 untouched ZfKD DatenBrowser exports
│   └── exportCSV-Export{A,B1,B2,C-*,D-*,E,F*}/
│       ├── Krebsdaten.csv
    └── metadaten.txt

```

## Quick-start

```bash
git clone https://github.com/rnmcln/cns-zfkd-c70-c72-2004-2023.git
cd cns-zfkd-c70-c72-2004-2023
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash run_all.sh
# outputs appear in ./tables, ./figures, ./data_tidy, ./analysis_results.json
```

## Canonical outputs

| Endpoint      | Sex | 2004 | 2023 | APC   | OLS 95% CI      | OLS p  | HAC(1) 95% CI     | HAC(1) p | DW   | MK Z   | MK p   | Theil-Sen slope |
|---------------|-----|------|------|-------|------------------|--------|--------------------|----------|------|--------|--------|------------------|
| Incidence ASR | F   | 5.7  | 5.0  | -0.44 | (-0.78, -0.10)  | 0.021  | (-0.89, +0.01)    | 0.058    | 0.96 | -2.236 | 0.025  | -0.0333          |
| Incidence ASR | M   | 8.0  | 7.2  | -0.37 | (-0.61, -0.13)  | 0.008  | (-0.77, +0.03)    | 0.068    | 0.79 | -2.518 | 0.012  | -0.0333          |
| Mortality ASR | F   | 4.2  | 3.7  | -0.54 | (-0.74, -0.34)  | <0.001 | (-0.81, -0.27)    | <0.001   | 2.28 | -3.583 | <0.001 | -0.0222          |
| Mortality ASR | M   | 6.1  | 5.6  | -0.23 | (-0.40, -0.04)  | 0.025  | (-0.42, -0.02)    | 0.029    | 1.42 | -2.141 | 0.032  | -0.0133          |

**Primary inference rule.** For the two incidence series, DW < 1 (0.96
female, 0.79 male) indicates positive residual autocorrelation; the
Newey-West HAC(1) 95% CIs are therefore the primary inference and both
cross zero (borderline p = 0.058, 0.068). Direction is corroborated by
the classical Mann-Kendall test (pymannkendall 1.4.3 `original_test`,
tau-a). For the two mortality series, DW (2.28, 1.42) is acceptable
and OLS and HAC(1) intervals concur.

## Data provenance

- **ZfKD DatenBrowser** (Robert Koch Institute, Berlin) — aggregate
  open-access tabulations retrieved **31 January 2025** from
  <https://www.krebsdaten.de>. No individual-level data.
- **Eurostat** — `hlth_cd_aro` (deaths) and `demo_pjangroup` (population)
  for external cross-validation and denominators (retrieved March 2026).

## Verification

```bash
# integrity of raw inputs
sha256sum -c CHECKSUMS.txt        # Linux
shasum -a 256 -c CHECKSUMS.txt    # macOS
```

## Licence

Code: MIT. Aggregate data: ZfKD terms (public-domain usage for
non-commercial research with source attribution).

## Contact

Aaron Lawson McLean — alawsonmclean@gmail.com
