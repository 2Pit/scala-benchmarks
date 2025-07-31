import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import os
import sys
from itertools import cycle

# Parse optional method suffix
method = sys.argv[1] if len(sys.argv) > 1 else None
filename = "bench.csv" if method is None else f"bench_{method}.csv"
plotname = "latency_n_nlogn.png" if method is None else f"latency_{method}_n_nlogn.png"
plotpath = os.path.join("plots", plotname)

# Load CSV
df = pd.read_csv(filename)
df["Param: size"] = pd.to_numeric(df["Param: size"], errors="coerce")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")  # already in ns/op
df["Score Error (99.9%)"] = pd.to_numeric(df["Score Error (99.9%)"], errors="coerce")

# Convert to latency and standard deviation
df["Latency"] = df["Score"]
df["Latency Std"] = df["Score Error (99.9%)"] / 3.29

# Prepare plot
base_colors = cycle(["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
plt.figure(figsize=(8, 5))
grouped = df.groupby("Benchmark")

for name, group in grouped:
    color = next(base_colors)
    group = group.sort_values("Param: size")
    x = group["Param: size"].values
    y = group["Latency"].values
    yerr = group["Latency Std"].values * 1.96  # 95% CI

    # Define features: x and x·log(x)
    x1 = x
    x2 = x * np.log(x)
    X = np.column_stack((x1, x2))
    X = sm.add_constant(X)

    weights = 1 / (yerr**2)
    model = sm.WLS(y, X, weights=weights)
    results = model.fit()

    # Predict on smooth range
    x_pred = np.linspace(x.min(), x.max(), 200)
    x1_pred = x_pred
    x2_pred = x_pred * np.log(x_pred)
    X_pred = sm.add_constant(np.column_stack((x1_pred, x2_pred)))
    pred = results.get_prediction(X_pred)
    pred_ci = pred.summary_frame(alpha=0.05)

    y_fit = pred_ci["mean"]
    ci_low = pred_ci["mean_ci_lower"]
    ci_high = pred_ci["mean_ci_upper"]

    label = name.split(".")[-1]

    # Plot points with error bars
    plt.errorbar(x, y, yerr=yerr, fmt='o', capsize=4, label=label, color=color)

    # Plot fit line
    plt.plot(x_pred, y_fit, linestyle='--', color=color)

    # Plot confidence band
    plt.fill_between(x_pred, ci_low, ci_high, alpha=0.2, color=color)

    # Print regression summary and RMSE
    a, b, c = results.params
    a_std, b_std, c_std = results.bse
    y_pred_actual = results.predict(X)
    rmse = np.sqrt(np.mean((y - y_pred_actual) ** 2))

    print(f"{label}: latency = ({a:.3f} ± {a_std:.3f}) + ({b:.3f} ± {b_std:.3f})·n + ({c:.3f} ± {c_std:.3f})·n·log(n)")
    print(f"{label}: RMSE = {rmse:.3f} ns/op\n")

# Final plot settings
plt.xlabel("Size")
plt.ylabel("Latency (nanoseconds per op)")
plt.grid(True, which='both')
plt.legend()
plt.title(f"Latency Fit with n + n·log(n) Model — {method or 'total'}")
plt.tight_layout()

# Save
os.makedirs("plots", exist_ok=True)
plt.savefig(plotpath)
plt.show()
