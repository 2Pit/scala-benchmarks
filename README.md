# Speedup Array Benchmark

This project is designed to benchmark and analyze the performance of various methods implemented in a Scala library for array transformations. It focuses on comparing different low-level implementations of `map`, `foreach`, and other traversal operations, aiming to detect performance differences depending on call site structure and compiler behavior.

We test performance of various methods applied to `Array[Int]`:
- [`map`](https://github.com/2Pit/scala-benchmarks/blob/main/src/main/scala/benchmarks/Impl.scala#L7-L36)
- [`foreach`](https://github.com/2Pit/scala-benchmarks/blob/main/src/main/scala/benchmarks/Impl.scala#L38-L61)

Full source code: [`Impl.scala`](https://github.com/2Pit/scala-benchmarks/blob/main/src/main/scala/benchmarks/Impl.scala)

## Running Benchmarks

Benchmarks are executed using `Makefile` targets. Each target runs a specific group of benchmarks via JMH. For example:

```
make bench_map_1
```

This command will:

- run JMH benchmarks with varying array sizes,
- store the results as CSV in `analysis/data/`,
- adjust measurement time depending on the input size.

## Analyzing Results

Analysis is performed using Python scripts inside the `analysis/` folder, relying on `pandas`, `statsmodels`, and `matplotlib`.

To run an analysis:

```
cd analysis
source venv/bin/activate
python ploty.py map_1
```

This script reads a benchmark result file (e.g., `bench_map_1.csv`), fits linear regression (latency vs size), and generates plots in `plots/`.

## GitHub Actions

The repository includes a GitHub Actions workflow for automated benchmarking:

- Workflow config: `.github/workflows/bench.yml`
- Benchmarks are run manually and their results are stored as workflow artifacts

You can trigger benchmarks manually or on every push via the **Actions** tab in the GitHub UI.

## Project Structure

```
.
├── analysis/          # Python scripts and benchmark output
├── review/            # Written reports and result summaries
├── project/           # sbt project files
├── src/               # Scala JMH benchmarks
├── .github/           # GitHub Actions workflow
├── Makefile           # Benchmark automation entrypoints
└── README.md
```

## Requirements

- Scala 3 and sbt
- JMH (via sbt plugin)
- Python 3

To set up the Python environment:

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
python ploty.py map_1
```

This will:
- run the benchmark for various array sizes,
- store the results in `analysis/data/bench_map_1.csv`,
- and produce a performance plot in `analysis/plots/`.
