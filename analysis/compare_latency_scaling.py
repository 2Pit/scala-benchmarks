import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm
import sys
import os

# Constants
CI_INPUT_LEVEL = 99.9
CI_INPUT_MULTIPLIER = 3.29
CI_OUTPUT_MULTIPLIER = 1.96

# Handle optional method argument (e.g., Map, ForEach)
method = sys.argv[1] if len(sys.argv) > 1 else None

filename = "bench.csv" if method is None else f"bench_{method}.csv"
plotname = "latency_scaling_wls.png" if method is None else f"latency_scaling_wls_{method}.png"
plotpath = os.path.join("plots", plotname)

# Read and prepare
df = pd.read_csv(filename)
df["Param: size"] = pd.to_numeric(df["Param: size"], errors="coerce")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
df["Score Error (99.9%)"] = pd.to_numeric(df["Score Error (99.9%)"], errors="coerce")

# Convert to standard deviation
df["Score Std"] = df["Score Error (99.9%)"] / CI_INPUT_MULTIPLIER
df["Latency"] = 1 / df["Score"]
df["Latency Std"] = df["Score Std"] / (df["Score"] ** 2)

# WLS regression
scaling_factors = []

print(f"\nApproximation: latency = a + k·size (WLS, 95% CI){' — ' + method if method else ''}:\n")

for name, group in df.groupby("Benchmark"):
    name_short = name.split(".")[-1]
    sizes = group["Param: size"].values
    latencies = group["Latency"].values
    stds = group["Latency Std"].values
    weights = 1 / (stds ** 2)

    X = sm.add_constant(sizes)
    model = sm.WLS(latencies, X, weights=weights)
    results = model.fit()

    intercept = results.params[0]
    slope = results.params[1]
    intercept_err = results.bse[0] * CI_OUTPUT_MULTIPLIER
    slope_err = results.bse[1] * CI_OUTPUT_MULTIPLIER

    scaling_factors.append((name_short, slope, results.bse[1], intercept))

    print(
        f"{name_short.ljust(20)} → latency(size) = "
        f"({intercept:.2e} ± {intercept_err:.1e}) + "
        f"({slope:.2e} ± {slope_err:.1e})·size"
    )

# Sort and extract
scaling_factors.sort(key=lambda x: x[0])
names  = [x[0] for x in scaling_factors]
slopes = [x[1] for x in scaling_factors]
errors = [x[2] * CI_OUTPUT_MULTIPLIER for x in scaling_factors]  # 95% CI

# Plot
plt.figure(figsize=(8, 5))
bars = plt.bar(names, slopes, yerr=errors, capsize=8, color="salmon", ecolor='black')
plt.ylabel("Slope k in: latency = a + k·size")
plt.title(f"Scalability estimate with 95% confidence intervals (WLS){' — ' + method if method else ''}")
plt.grid(axis="y")

for bar, slope, err in zip(bars, slopes, errors):
    y = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        y + max(errors) * 0.5,
        f"{slope:.2e}",
        ha='center',
        fontsize=9,
    )

plt.tight_layout()
os.makedirs("plots", exist_ok=True)
plt.savefig(plotpath)

# --- Pairwise slope comparison (if prefixes match) ---
print("\nPairwise hypothesis test (prefix match): are slopes significantly different (p < 0.01)?\n")

for i in range(len(scaling_factors)):
    for j in range(i + 1, len(scaling_factors)):
        name_i, slope_i, stderr_i, _ = scaling_factors[i]
        name_j, slope_j, stderr_j, _ = scaling_factors[j]

        if name_i[2:] != name_j[2:]:
            continue

        diff = slope_i - slope_j
        std_err = np.sqrt(stderr_i**2 + stderr_j**2)
        z = diff / std_err
        p = 2 * (1 - norm.cdf(abs(z)))

        verdict = "YES" if p < 0.01 else "NO"
        print(f"{name_i} vs {name_j}".ljust(35) + f"p = {p:.4f} → significantly different? {verdict}")

plt.show()
