#!/usr/bin/env python3
"""
Trend analysis for CNS tumour (ICD-10 C70-C72) registry data from ZfKD.
Computes OLS regression, log-linear APC with 95% CIs, Mann-Kendall test,
and Theil-Sen robust slope for age-standardised incidence and mortality rates.

Study period: 2004-2023 (20 calendar years).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

DATA_DIR = Path(__file__).resolve().parent.parent / "data_tidy"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "analysis_results.json"

YEAR_MIN, YEAR_MAX = 2004, 2023


def load_asr_series(csv_path: Path, year_min: int, year_max: int) -> pd.DataFrame:
    """Load tidy CSV and filter to ASR rows within the study period."""
    df = pd.read_csv(csv_path)
    mask = (
        (df["kennzahl"].str.contains("Altersstandardisierte", case=False, na=False))
        & (df["year"] >= year_min)
        & (df["year"] <= year_max)
    )
    return df.loc[mask].copy()


def run_trend_analysis(years: np.ndarray, rates: np.ndarray) -> dict:
    """Run all four trend methods on a single ASR time series."""
    n = len(years)
    assert n == (YEAR_MAX - YEAR_MIN + 1), f"Expected {YEAR_MAX - YEAR_MIN + 1} points, got {n}"

    # 1. OLS linear regression
    X = sm.add_constant(years)
    ols_model = sm.OLS(rates, X).fit()
    slope = ols_model.params[1]
    se = ols_model.bse[1]
    r2 = ols_model.rsquared
    p_lin = ols_model.f_pvalue

    # 2. Log-linear regression -> APC with 95% CI
    log_rates = np.log(rates)
    log_model = sm.OLS(log_rates, X).fit()
    beta = log_model.params[1]
    beta_se = log_model.bse[1]
    apc = (np.exp(beta) - 1) * 100
    apc_lo = (np.exp(beta - 1.96 * beta_se) - 1) * 100
    apc_hi = (np.exp(beta + 1.96 * beta_se) - 1) * 100
    p_apc = log_model.pvalues[1]

    # 3. Mann-Kendall trend test
    # Canonical: classical (tau-a) via pymannkendall
    import pymannkendall as pmk  # pinned in requirements.txt
    mk_classic = pmk.original_test(rates)
    Z_mk = mk_classic.z
    p_mk = mk_classic.p

    # Auxiliary: tau-b derived S from scipy (reported as sensitivity)
    mk_taub = stats.kendalltau(years, rates)
    S_taub = mk_taub.statistic * n * (n - 1) / 2
    var_S = n * (n - 1) * (2 * n + 5) / 18
    if S_taub > 0:
        Z_taub = (S_taub - 1) / np.sqrt(var_S)
    elif S_taub < 0:
        Z_taub = (S_taub + 1) / np.sqrt(var_S)
    else:
        Z_taub = 0.0
    p_taub = 2 * stats.norm.sf(abs(Z_taub))

    # 4. Theil-Sen robust slope
    ts = stats.theilslopes(rates, years)
    ts_slope = ts.slope
    ts_lo = ts.low_slope
    ts_hi = ts.high_slope

    return {
        "linear_slope": round(slope, 4),
        "linear_se": round(se, 4),
        "linear_r2": round(r2, 4),
        "linear_p": round(p_lin, 6),
        "log_slope": round(beta, 6),
        "APC": round(apc, 2),
        "APC_CI95": [round(apc_lo, 2), round(apc_hi, 2)],
        "APC_p": round(p_apc, 6),
        "MK_Z": round(Z_mk, 3),
        "MK_p": round(p_mk, 6),
        "MK_Z_taub_aux": round(Z_taub, 3),
        "MK_p_taub_aux": round(p_taub, 6),
        "TheilSen_slope": round(ts_slope, 4),
        "TheilSen_CI95": [round(ts_lo, 4), round(ts_hi, 4)],
    }


def main():
    results = {}

    # --- Incidence ---
    inc = load_asr_series(DATA_DIR / "incidence_tidy.csv", YEAR_MIN, YEAR_MAX)
    for sex in ["weiblich", "männlich"]:
        sub = inc[inc["sex"] == sex].sort_values("year")
        key = f"inc_asr_{sex}"
        results[key] = run_trend_analysis(sub["year"].values, sub["value"].values)
        print(f"{key}: APC = {results[key]['APC']}% "
              f"(95% CI: {results[key]['APC_CI95'][0]}% to {results[key]['APC_CI95'][1]}%), "
              f"p = {results[key]['APC_p']}")

    # --- Mortality ---
    mort = load_asr_series(DATA_DIR / "mortality_tidy.csv", YEAR_MIN, YEAR_MAX)
    for sex in ["weiblich", "männlich"]:
        sub = mort[mort["sex"] == sex].sort_values("year")
        key = f"mort_asr_{sex}"
        results[key] = run_trend_analysis(sub["year"].values, sub["value"].values)
        print(f"{key}: APC = {results[key]['APC']}% "
              f"(95% CI: {results[key]['APC_CI95'][0]}% to {results[key]['APC_CI95'][1]}%), "
              f"p = {results[key]['APC_p']}")

    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
