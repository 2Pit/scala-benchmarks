"""
Latency Benchmark Regression Plotter

This script reads benchmark data from a CSV file, performs weighted linear regression
for each benchmark series (latency vs. input size), and visualizes the results using Plotly.

Key features:
- Supports optional command-line suffix to select different input files.
- Converts latency measurements from throughput scores and error margins.
- Applies weighted least squares (WLS) regression using inverse variance weights.
- Plots:
    • Raw data with error bars
    • Regression lines with 95% confidence intervals
- Compares slopes (latency per unit size) between all benchmark pairs using a two-sided z-test.
  Prints p-values and highlights statistically significant differences.

Constants such as confidence levels, directories, and thresholds are configurable at the top.

Usage:
    make init
    source venv/bin/activate
    make update

    python ploty.py [suffix]   # Uses 'bench[_suffix].csv'

Output:
- Interactive HTML plot saved to ./plots/latency_[method]_linear.html
- Console output with regression equations and slope comparison results
"""


import pandas as pd
import numpy as np
import statsmodels.api as sm
import plotly.graph_objects as go
import os
import sys
from itertools import cycle, combinations
import plotly.express as px
from scipy import stats

# === Constants ===
ALPHA = 0.05                     # Significance level for confidence intervals
P_VALUE_THRESHOLD = 0.01         # Threshold for pairwise slope comparison
CI_MULTIPLIER = 1.96             # 95% confidence interval multiplier
Z_999 = 3.29                     # z-score for 99.9% confidence interval
DEFAULT_DATA_DIR = "data"
PLOT_DIR = "plots"
LATENCY_CI_OPACITY = 0.2         # Opacity for CI bands
LATENCY_CI_BAND_ALPHA = 0.15     # RGBA band alpha channel

# === Parse CLI Argument ===
method = sys.argv[1] if len(sys.argv) > 1 else None
filename = "bench.csv" if method is None else f"bench_{method}.csv"
basename = "latency" if method is None else f"latency_{method}"
html_path = os.path.join(PLOT_DIR, f"{basename}.html")

# === Load and Prepare Data ===
df = pd.read_csv(os.path.join(DEFAULT_DATA_DIR, filename))
df["Param: size"] = pd.to_numeric(df["Param: size"], errors="coerce")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
df["Score Error (99.9%)"] = pd.to_numeric(df["Score Error (99.9%)"], errors="coerce")

df["Latency"] = df["Score"]
df["Latency Std"] = df["Score Error (99.9%)"] / Z_999
df["Latency CI"] = df["Latency Std"] * CI_MULTIPLIER

# === Plot Setup ===
fig = go.Figure()
colors = px.colors.qualitative.Plotly
color_cycle = cycle(colors)

# === Regression Analysis ===
regression_results = []

for name, group in df.groupby("Benchmark"):
    color = next(color_cycle)
    group = group.sort_values("Param: size")
    x = group["Param: size"].values
    y = group["Latency"].values
    yerr = group["Latency CI"].values
    label = name.split(".")[-1]

    # Weighted linear regression
    X = sm.add_constant(x)
    weights = 1 / (yerr**2)
    model = sm.WLS(y, X, weights=weights)
    results = model.fit()

    # Predictions and CI
    x_pred = np.logspace(np.log10(x.min()), np.log10(x.max()), 200)
    X_pred = sm.add_constant(x_pred)
    pred = results.get_prediction(X_pred).summary_frame(alpha=ALPHA)
    y_fit = pred["mean"]
    ci_low = pred["mean_ci_lower"]
    ci_high = pred["mean_ci_upper"]

    # Plot: data points
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers", name=label,
        error_y=dict(type="data", array=yerr, visible=True, color=color),
        marker=dict(color=color)
    ))

    # Plot: regression line
    fig.add_trace(go.Scatter(
        x=x_pred, y=y_fit, mode="lines", name=f"{label} fit",
        line=dict(color=color, dash="dash")
    ))

    # Plot: confidence band
    fill_rgba = color.replace('rgb', 'rgba').replace(')', f',{LATENCY_CI_BAND_ALPHA})')
    fig.add_trace(go.Scatter(
        x=np.concatenate([x_pred, x_pred[::-1]]),
        y=np.concatenate([ci_low, ci_high[::-1]]),
        fill='toself',
        fillcolor=color,
        opacity=LATENCY_CI_OPACITY,
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False
    ))

    # Extract regression stats
    a, b = results.params
    a_std, b_std = results.bse
    y_pred_actual = results.predict(X)
    rmse = np.sqrt(np.mean((y - y_pred_actual) ** 2))

    regression_results.append({
        "label": label,
        "slope": b,
        "slope_std": b_std,
        "intercept": a,
        "rmse": rmse
    })

    print(f"{label}: latency = ({a:.3f} ± {a_std:.3f}) + ({b:.3f} ± {b_std:.3f}) · size    "
          f"[RMSE = {rmse:.3f} ns/op]")

# === Pairwise slope comparison ===
print("\nPairwise slope comparisons:")
for (r1, r2) in combinations(regression_results, 2):
    delta = r1["slope"] - r2["slope"]
    pooled_std = np.sqrt(r1["slope_std"] ** 2 + r2["slope_std"] ** 2)
    t_stat = delta / pooled_std
    p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    significant = "YES" if p_value < P_VALUE_THRESHOLD else "NO"
    print(f"{r1['label']} vs {r2['label']}: Δslope = {delta:.4f}, p = {p_value:.4f} → significantly different? {significant}")

# === Final Plot Layout ===
fig.update_layout(
    title=f"Latency Linear Regression with {int((1 - ALPHA) * 100)}% Confidence Bands — {method or 'total'}",
    xaxis=dict(
        title="Size",
        type="log",
        ticks="outside",
        tickformat=".0f",
        minor=dict(ticks="outside", showgrid=True),
        showgrid=True,
        gridwidth=1
    ),
    yaxis=dict(
        title="Latency (nanoseconds per op)",
        type="log",
        ticks="outside",
        tickformat=".0f",
        minor=dict(ticks="outside", showgrid=True),
        showgrid=True,
        gridwidth=1
    ),
    legend_title="Benchmark",
    template="plotly_white"
)

# === Save Plot ===
os.makedirs(PLOT_DIR, exist_ok=True)
fig.write_html(html_path)
fig.show()
