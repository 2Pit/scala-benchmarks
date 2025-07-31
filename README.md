# Speedup Array Benchmark

This project is designed to benchmark and analyze the performance of various methods implemented in a Scala library for array transformations. It focuses on comparing different implementations of `map`, `foreach`, and similar operations.

## Running Benchmarks

Benchmarks are executed via a `Makefile`. Each target corresponds to a specific group of benchmarks. For example:

```make bench_map_1```

This command will:

- run JMH benchmarks with varying array sizes,
- store the results as a CSV file in the `analysis/` directory,
- adjust measurement time depending on the input size.

## Analyzing Results

Analysis is performed using Python scripts with `matplotlib`, `pandas`, and `statsmodels`.

1. Activate the virtual environment (if not already active):

```
cd analysis
source venv/bin/activate
```

2. Generate a latency plot for a benchmark:

```python plot_latency.py map_1```

This script reads the corresponding CSV (e.g., `bench_map_1.csv`), performs regression, and saves a plot to the `plots/` directory.

## Project Structure

```
.
├── analysis/          # Python scripts and benchmark output
│   ├── bench_map_1.csv
│   ├── plot_latency.py
│   └── plots/
├── project/           # sbt project files
├── src/               # Scala JMH benchmarks
├── Makefile           # Benchmark automation
└── README.md
```

## Requirements

- Scala 3 and sbt
- JMH (configured via sbt plugin)
- Python 3 with the following packages:
  - `pandas`
  - `matplotlib`
  - `statsmodels`
  - `scikit-learn`

To install Python dependencies:

```
cd analysis
python -m venv venv
source venv/bin/activate
make update
```

## Example Workflow

```
make bench_map_1

cd analysis
python plot_latency.py map_1
```

This will run the benchmark for various array sizes, store the results in `analysis/bench_map_1.csv`, and produce a performance plot.
