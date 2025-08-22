package benchmarks

import org.openjdk.jmh.annotations._
import org.openjdk.jmh.infra.Blackhole
import java.util.concurrent.TimeUnit
import benchmarks.ArrayOpsCompat._
// import scala.compiletime.uninitialized

import scala.reflect.ClassTag

@State(Scope.Thread)
@BenchmarkMode(Array(Mode.AverageTime))
@OutputTimeUnit(TimeUnit.NANOSECONDS)
class MapBenchmark {

  // @Param(Array("1", "4", "8", "16", "32", "64", "128", "256", "512", "1000", "10000"))
  @Param(Array("8", "128", "1024"))
  var size: Int = _

  var array: Array[Int] = _

  @Setup
  def setup(): Unit = {
    array = Array.fill(size)(1)
  }

  def heavy(x: Int): Int = Math.sqrt(x.toDouble).toInt

  @Benchmark
  def old_map_1(bh: Blackhole): Unit =
    bh.consume(array.oldMap(heavy))

  @Benchmark
  def new_map_1(bh: Blackhole): Unit =
    bh.consume(array.newMap(heavy))
}
