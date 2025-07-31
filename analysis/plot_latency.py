import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import os
import sys
from itertools import cycle

# Parse optional method suffix from command-line arguments
method = sys.argv[1] if len(sys.argv) > 1 else None
filename = "bench.csv" if method is None else f"bench_{method}.csv"
plotname = "latency_linear.png" if method is None else f"latency_{method}_linear.png"
plotpath = os.path.join("plots", plotname)

# Load CSV and parse numeric values
df = pd.read_csv(filename)
df["Param: size"] = pd.to_numeric(df["Param: size"], errors="coerce")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")  # in nanoseconds per op
df["Score Error (99.9%)"] = pd.to_numeric(df["Score Error (99.9%)"], errors="coerce")

# Estimate standard deviation assuming 99.9% CI ≈ 3.29σ
df["Latency"] = df["Score"]
df["Latency Std"] = df["Score Error (99.9%)"] / 3.29

# Define color palette
base_colors = cycle(["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])

plt.figure(figsize=(8, 5))
grouped = df.groupby("Benchmark")

for name, group in grouped:
    color = next(base_colors)
    group = group.sort_values("Param: size")
    x = group["Param: size"].values
    y = group["Latency"].values
    yerr = group["Latency Std"].values * 1.96  # Convert to 95% CI

    # Linear regression with intercept: y = a + b·x
    X = sm.add_constant(x)  # Adds a column of ones for intercept
    weights = 1 / yerr**2
    model = sm.WLS(y, X, weights=weights)
    results = model.fit()

    # Generate predictions and 95% CI
    x_pred = np.linspace(x.min(), x.max(), 200)
    X_pred = sm.add_constant(x_pred)
    pred = results.get_prediction(X_pred)
    pred_ci = pred.summary_frame(alpha=0.05)

    y_fit = pred_ci["mean"]
    ci_low = pred_ci["mean_ci_lower"]
    ci_high = pred_ci["mean_ci_upper"]

    label = name.split(".")[-1]

    # Plot points with error bars
    plt.errorbar(x, y, yerr=yerr, fmt='o', capsize=4, label=label, color=color)

    # Plot regression line and confidence band
    plt.plot(x_pred, y_fit, linestyle='--', color=color)
    plt.fill_between(x_pred, ci_low, ci_high, alpha=0.2, color=color)

    # Output model parameters and RMSE
    a, b = results.params
    a_std, b_std = results.bse
    y_pred_actual = results.predict(X)
    rmse = np.sqrt(np.mean((y - y_pred_actual) ** 2))

    print(f"{label}: latency = ({a:.3f} ± {a_std:.3f}) + ({b:.3f} ± {b_std:.3f}) · size    [RMSE = {rmse:.3f} ns/op]")

# Axis and plot formatting
plt.xlabel("Size")
plt.ylabel("Latency (nanoseconds per op)")
plt.grid(True, which='both')
plt.legend()
plt.title(f"Latency Linear Regression with Intercept — {method or 'total'}")
plt.tight_layout()

# To enable logarithmic axes, uncomment one or both lines below:
# plt.xscale("log")  # X-axis in log scale
# plt.yscale("log")  # Y-axis in log scale

# Save plot
os.makedirs("plots", exist_ok=True)
plt.savefig(plotpath)
plt.show()
