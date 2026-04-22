# Project and Results Summary (v2)

## Project

A fully reproducible, multi-endpoint descriptive epidemiology of
malignant central nervous system tumours (ICD-10-GM C70-C72) in Germany
across two decades (2004-2023), using aggregate open-access exports
from the ZfKD DatenBrowser at the Robert Koch Institute. Four
complementary endpoints are reported in parallel for the first time
for Germany: age-standardised incidence, age-standardised mortality,
five-year period relative survival (Ederer II), and five-year
limited-duration prevalence.

## Design

- **Case definition**: ICD-10-GM C70 (malignant meninges), C71
  (malignant brain), C72 (malignant spinal cord, cranial nerves, other
  CNS), extracted as the mandatory combined group by the DatenBrowser
  interface.
- **Study window**: 2004-2023 (20 calendar years), selected on ZfKD
  recommendation to mitigate early-registry incompleteness.
- **Stratifications**: sex; age (15-44, 45-54, 55-64, 65-74, >=75
  years; plus 0-44 for prevalence).
- **Primary trend model**: log-linear regression of ASR on calendar
  year, yielding annual percentage change (APC) with 95% CI
  back-transformed from the Wald CI of the log-slope.
- **Primary inference for incidence (v2)**: Newey-West HAC(1) standard
  errors (statsmodels 0.14.2). Positive residual autocorrelation was
  detected (Durbin-Watson 0.96 [female] and 0.79 [male]), justifying
  autocorrelation-robust inference.
- **Sensitivity analyses** (pre-specified): ordinary least squares
  (slope / SE / R^2); classical Mann-Kendall (tau-a;
  `pymannkendall.original_test`); Theil-Sen robust slope.
- **Period survival**: Ederer II relative survival (Brenner and
  Gefeller, 1996), eight diagnostic periods 2007-2008 through
  2021-2023.
- **External validation**: Eurostat cause-of-death (`hlth_cd_aro`)
  2011-2023 compared against ZfKD mortality series.

## Headline findings (v2)

1. **Declining age-standardised rates — incidence borderline, mortality
   robust.** Incidence ASR fell from 5.7 to 5.0 per 100,000 in females
   (APC -0.44%, OLS p = 0.021, HAC(1) p = 0.058) and from 8.0 to 7.2
   in males (APC -0.37%, OLS p = 0.008, HAC(1) p = 0.068). Under the
   primary HAC(1) inference the incidence declines are borderline;
   direction is corroborated by Mann-Kendall (Z = -2.24, -2.52; both
   p < 0.05) and Theil-Sen. Mortality ASR declines are robust: female
   APC -0.54% (HAC(1) p < 0.001), male APC -0.23% (HAC(1) p = 0.029).
2. **Rising absolute burden.** Despite declining ASR, absolute burden
   rose to 6,560 incident cases (aged 15+) and 5,985 deaths (all ages)
   in 2023. Five-year limited-duration prevalence rose +62% (F) and
   +70% (M) in the >=75 stratum, driven predominantly by population
   ageing (the German population aged >=75 grew by 43% over the same
   window, Eurostat `demo_pjangroup`).
3. **Static population-level survival.** Five-year relative survival
   remained in the 30-35% (F) / 26-29% (M) band across all eight
   diagnostic periods; inter-period changes are within +/- 3-5
   percentage points with no consistent direction. Formal inference
   across periods is precluded by the absence of registry-supplied
   standard errors.
4. **MIR stability.** The ASR-based mortality-to-incidence ratio
   fluctuated between 0.63-0.77 (F) and 0.69-0.78 (M) with no
   systematic trend, consistent with the incidence-driven
   interpretation of the ASR declines. Interpretation of the MIR as an
   informal fatality index assumes approximate steady state, which is
   noted as a limitation.

## Interpretation

The dissociation between falling rates and rising absolute burden,
with static population survival despite trial-reported therapeutic
advances, is consistent with a tumour aggregate dominated by
glioblastoma, IDH-wildtype (WHO CNS 2021) in adults — a histology
whose case-fatality has barely shifted at the population level despite
Stupp-era and subsequent advances. The ICD-10 topographic grouping
obscures biological heterogeneity; histology-specific,
molecular-integrated registry data aligned with WHO CNS 2021 are
needed to interpret the drivers of these patterns.

## Limitations at a glance

Aggregated topographic-only data; no histology or morphology; no
individual records; no registry-supplied standard errors on survival;
period method susceptible to lead-time bias; registry completeness
changes in early years; MIR imprecision from 1-decimal-place ASR
rounding; suppression of small strata.

## Reproducibility

All figures, tables, and numerical claims in the manuscript regenerate
deterministically from the raw ZfKD CSVs in `data_raw/` via the single
entry point `bash run_all.sh`. Software environment pinned in
`requirements.txt`. Checksums in `CHECKSUMS.txt`. Drift guard
(`src/render_docx_stub.py`) asserts manuscript numbers against
`analysis_results.json` before release. Full audit trail (v2
discrepancies report, six-round peer review, corrected Harvard-style
references) is in `audit/`.
