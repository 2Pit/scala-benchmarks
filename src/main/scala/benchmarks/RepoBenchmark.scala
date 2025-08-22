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
class RepoBenchmark {

  @Param(Array("8", "128", "1024"))
  var size: Int = _

  var integers: List[Int] = _
  var integersA: Array[Int] = _
  var intIntA: Array[Array[Int]] = _

  @Setup
  def setup(): Unit = {
    integers = (1 to size).toList
    integersA = integers.toArray
    intIntA = integersA.map { x => integersA }
  }

  def heavy(x: Int): Int = Math.sqrt(x.toDouble).toInt

  @Benchmark def old_mapIntInt(bh: Blackhole): Unit =
    bh.consume(integersA.oldMap(x => 0))

  @Benchmark def old_mapIntString(bh: Blackhole): Unit =
    bh.consume(integersA.oldMap(x => ""))

  @Benchmark def new_mapIntInt(bh: Blackhole): Unit =
    bh.consume(integersA.newMap(x => 0))

  @Benchmark def new_mapIntString(bh: Blackhole): Unit =
    bh.consume(integersA.newMap(x => ""))
}
