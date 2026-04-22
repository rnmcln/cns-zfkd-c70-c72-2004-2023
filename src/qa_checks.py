import numpy as np
import pandas as pd

def linear_slope_lstsq(years, values):
    x = np.asarray(years, dtype=float)
    y = np.asarray(values, dtype=float)
    A = np.vstack([x, np.ones(len(x))]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(slope), float(intercept)

def linear_slope_formula(years, values):
    x = list(map(float, years))
    y = list(map(float, values))
    xbar = sum(x) / len(x)
    ybar = sum(y) / len(y)
    num = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y))
    den = sum((xi - xbar) ** 2 for xi in x)
    return float(num / den) if den != 0 else np.nan

def yoy_diff_pandas(values):
    return list(pd.Series(values).diff().iloc[1:].to_numpy())

def yoy_diff_loop(values):
    return [values[i] - values[i - 1] for i in range(1, len(values))]
