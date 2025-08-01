FORKS := 1

# SIZES_SHORT := 0,1,4,8,16,32,64,128,256,512
SIZES_SHORT := 1,4,16,128,512
SIZES_LONG  := 1000,10000

WARMUP_ITER        := 4
WARMUP_TIME_SHORT  := 1s
WARMUP_TIME_LONG   := 2s

MEASURE_ITER       := 6
MEASURE_TIME_SHORT := 3s
MEASURE_TIME_LONG  := 20s

# private
bench.run:
	@echo "Running ${BENCH_CLASS} → ${RESULT_FILE}"; \
	rm -f ${RESULT_FILE} ${RESULT_FILE}.tmp; \
	echo "Short sizes..."; \
	sbt "jmh:run -i $(MEASURE_ITER) -wi $(WARMUP_ITER) -r $(MEASURE_TIME_SHORT) -w $(WARMUP_TIME_SHORT) -f$(FORKS) -t1 \".*${BENCH_CLASS}.*\" -p size=$(SIZES_SHORT) -rf csv -rff ${RESULT_FILE}" || exit $$?; \
	echo "Long sizes..."; \
	sbt "jmh:run -i $(MEASURE_ITER) -wi $(WARMUP_ITER) -r $(MEASURE_TIME_LONG) -w $(WARMUP_TIME_LONG) -f$(FORKS) -t1 \".*${BENCH_CLASS}.*\" -p size=$(SIZES_LONG) -rf csv -rff ${RESULT_FILE}.tmp" || exit $$?; \
	tail -n +2 ${RESULT_FILE}.tmp >> ${RESULT_FILE}; \
	rm -f ${RESULT_FILE}.tmp

bench_map_1:
	$(MAKE) bench.run BENCH_CLASS=MapBenchmark RESULT_FILE=analysis/data/bench_map_1.csv

bench_map_3:
	$(MAKE) bench.run BENCH_CLASS=Map3Benchmark RESULT_FILE=analysis/data/bench_map_3.csv

bench_map_1_lam:
	$(MAKE) bench.run BENCH_CLASS=MapLamBenchmark RESULT_FILE=analysis/data/bench_map_1_lam.csv

bench_foreach:
	$(MAKE) bench.run BENCH_CLASS=ForeachBenchmark RESULT_FILE=analysis/data/bench_foreach.csv

bench_foreach_lam:
	$(MAKE) bench.run BENCH_CLASS=ForeachLamBenchmark RESULT_FILE=analysis/data/bench_foreach_lam.csv

bench_all: bench_map_1 bench_map_1_lam bench_foreach bench_foreach_lam

bench_custom: bench_map_1 bench_map_3 bench_foreach
