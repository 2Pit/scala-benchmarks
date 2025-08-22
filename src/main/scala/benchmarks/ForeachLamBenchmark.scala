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
class ForeachLamBenchmark {

  @Param(Array("1", "10", "100", "10000"))
  var size: Int = _

  var array: Array[Int] = _

  @Setup
  def setup(): Unit = {
    array = Array.fill(size)(1)
  }

  def heavy(x: Int): Int = Math.sqrt(x.toDouble).toInt

  @Benchmark
  def old_foreach(bh: Blackhole): Unit =
    array.oldForeach(x => bh.consume(heavy(x)))

  @Benchmark
  def new_foreach(bh: Blackhole): Unit =
    array.newForeach(x => bh.consume(heavy(x)))
}
