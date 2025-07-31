# Размеры
SIZES_SHORT := 1,4,8,16,32,64,128,256,512
SIZES_LONG  := 1000,10000

# Время выполнения для маленьких и больших сайзов
WARMUP_ITER      := 2
WARMUP_TIME_SHORT  := 1s
WARMUP_TIME_LONG   := 4s

MEASURE_ITER     := 6
MEASURE_TIME_SHORT := 2s
MEASURE_TIME_LONG  := 20s

# Кол-во форков
FORKS := 1

# Целевой CSV
RESULT_FILE := analysis/bench_map_1.csv
RESULT_TMP  := analysis/bench_map_1.tmp.csv

# Основная цель
bench_map_1:
	rm -f $(RESULT_FILE) $(RESULT_TMP); \
	echo "Running short sizes..."; \
	sbt 'jmh:run -i $(MEASURE_ITER) -wi $(WARMUP_ITER)
	             -r $(MEASURE_TIME_SHORT) -w $(WARMUP_TIME_SHORT)
	             -f$(FORKS) -t1
	             ".*MapBenchmark.*"
	             -p size=$(SIZES_SHORT)
	             -rf csv -rff $(RESULT_FILE)' || exit $$?; \
	echo "Running long sizes..."; \
	sbt 'jmh:run -i $(MEASURE_ITER) -wi $(WARMUP_ITER)
	             -r $(MEASURE_TIME_LONG) -w $(WARMUP_TIME_LONG)
	             -f$(FORKS) -t1
	             ".*MapBenchmark.*"
	             -p size=$(SIZES_LONG)
	             -rf csv -rff $(RESULT_TMP)' || exit $$?; \
	tail -n +2 $(RESULT_TMP) >> $(RESULT_FILE); \
	rm -f $(RESULT_TMP)
