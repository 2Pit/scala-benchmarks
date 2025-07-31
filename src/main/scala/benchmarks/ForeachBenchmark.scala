package benchmarks

import org.openjdk.jmh.annotations.*
import org.openjdk.jmh.infra.Blackhole
import java.util.concurrent.TimeUnit
import scala.compiletime.uninitialized

import scala.reflect.ClassTag

@State(Scope.Thread)
@BenchmarkMode(Array(Mode.AverageTime))
@OutputTimeUnit(TimeUnit.NANOSECONDS)
class ForeachBenchmark:

  @Param(Array("0", "1", "10", "100", "10000"))
  var size: Int = uninitialized

  var array: Array[Int] = uninitialized

  @Setup
  def setup(): Unit = {
    array = Array.fill(size)(1)
    System.gc()
    Thread.sleep(400) // чтобы GC успел пройти
  }

  def heavy(x: Int): Int = Math.sqrt(x.toDouble).toInt

  @Benchmark
  def old_foreach(bh: Blackhole): Unit =
    array.oldForeach(heavy.andThen(bh.consume))

  @Benchmark
  def new_foreach(bh: Blackhole): Unit =
    array.newForeach(heavy.andThen(bh.consume))
