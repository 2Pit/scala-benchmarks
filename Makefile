JFR_OUT      ?= benchmark.jfr
WARMUP_ITER  ?= 2
MEASURE_ITER ?= 3
WARMUP_TIME  ?= 1s
MEASURE_TIME ?= 5s
FORKS        ?= 1

# JMH_REGEX    ?= .*FlatMappedIntBenchmark.*map.*
JMH_REGEX    ?= .*ArrayBenchmark.flatMap3

jfr:
	rm -f $(JFR_OUT)
	sbt ';clean;compile;jmh:run -i $(MEASURE_ITER) \
	    -wi $(WARMUP_ITER) \
	    -r $(MEASURE_TIME) \
	    -w $(WARMUP_TIME) \
	    -f$(FORKS) \
	    -t1 \
	    -jvmArgs "-XX:+FlightRecorder -XX:StartFlightRecording=filename=$(JFR_OUT),dumponexit=true,settings=profile,stackdepth=128" \
	    $(JMH_REGEX)'
	open -a "JDK Mission Control" $(JFR_OUT)

bench_map:
	@JMH_REGEX='.*MapBenchmark.*'; \
	sbt ';clean;compile;jmh:run -i $(MEASURE_ITER) \
	             -wi $(WARMUP_ITER) \
	             -r $(MEASURE_TIME) \
	             -w $(WARMUP_TIME) \
	             -f$(FORKS) \
	             -t1 \
	             '$$JMH_REGEX' \
	             -rf csv -rff analysis/bench.csv'


bench_foreach:
	@JMH_REGEX='.*ForeachBenchmark.*'; \
	sbt ';clean;compile;jmh:run -i $(MEASURE_ITER) \
	             -wi $(WARMUP_ITER) \
	             -r $(MEASURE_TIME) \
	             -w $(WARMUP_TIME) \
	             -f$(FORKS) \
	             -t1 \
	             '$$JMH_REGEX' \
	             -rf csv -rff /dev/stdout'
