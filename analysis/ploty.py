import pandas as pd
import numpy as np
import statsmodels.api as sm
import plotly.graph_objects as go
import os
import sys
from itertools import cycle
import plotly.express as px

# Parse optional method suffix
method = sys.argv[1] if len(sys.argv) > 1 else None
filename = "bench.csv" if method is None else f"bench_{method}.csv"
basename = "latency_linear" if method is None else f"latency_{method}_linear"
html_path = os.path.join("plots", f"{basename}.html")
png_path = os.path.join("plots", f"{basename}.png")

# Load CSV
df = pd.read_csv("data/" + filename)
df["Param: size"] = pd.to_numeric(df["Param: size"], errors="coerce")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
df["Score Error (99.9%)"] = pd.to_numeric(df["Score Error (99.9%)"], errors="coerce")

# Convert to latency and estimate 95% CI
df["Latency"] = df["Score"]
df["Latency Std"] = df["Score Error (99.9%)"] / 3.29
df["Latency CI"] = df["Latency Std"] * 1.96

# Prepare plot
fig = go.Figure()
colors = px.colors.qualitative.Plotly
color_cycle = cycle(colors)

for name, group in df.groupby("Benchmark"):
    color = next(color_cycle)
    group = group.sort_values("Param: size")
    x = group["Param: size"].values
    y = group["Latency"].values
    yerr = group["Latency CI"].values
    label = name.split(".")[-1]

    # Fit weighted linear regression with intercept
    X = sm.add_constant(x)
    weights = 1 / (yerr**2)
    model = sm.WLS(y, X, weights=weights)
    results = model.fit()

    # Generate regression predictions and CI
    x_pred = np.logspace(np.log10(x.min()), np.log10(x.max()), 200)
    # x_pred = np.linspace(x.min(), x.max(), 200)
    X_pred = sm.add_constant(x_pred)
    pred = results.get_prediction(X_pred).summary_frame(alpha=0.05)
    y_fit = pred["mean"]
    ci_low = pred["mean_ci_lower"]
    ci_high = pred["mean_ci_upper"]

    # Plot data points with error bars
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers", name=label,
        error_y=dict(type="data", array=yerr, visible=True, color=color),
        marker=dict(color=color)
    ))

    # Plot regression line
    fig.add_trace(go.Scatter(
        x=x_pred, y=y_fit, mode="lines", name=f"{label} fit",
        line=dict(color=color, dash="dash")
    ))

    # Plot confidence interval as transparent band
    fill_rgba = color.replace('rgb', 'rgba').replace(')', ',0.15)')  # 15% opacity
    fig.add_trace(go.Scatter(
        x=np.concatenate([x_pred, x_pred[::-1]]),
        y=np.concatenate([ci_low, ci_high[::-1]]),
        fill='toself',
        fillcolor=color,  # keep RGB
        opacity=0.2,      # << ключевая строка
        line=dict(color='rgba(255,255,255,0)'),  # прозрачная рамка
        showlegend=False
    ))

    # Console output
    a, b = results.params
    a_std, b_std = results.bse
    y_pred_actual = results.predict(X)
    rmse = np.sqrt(np.mean((y - y_pred_actual) ** 2))
    print(f"{label}: latency = ({a:.3f} ± {a_std:.3f}) + ({b:.3f} ± {b_std:.3f}) · size    [RMSE = {rmse:.3f} ns/op]")

# Layout
fig.update_layout(
    title=f"Latency Linear Regression with Intercept — {method or 'total'}",
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

# Save
os.makedirs("plots", exist_ok=True)
fig.write_html(html_path)
# fig.write_image(png_path, width=900, height=600)
fig.show()
