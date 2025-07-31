package benchmarks

import org.openjdk.jmh.annotations.*
import org.openjdk.jmh.infra.Blackhole
import java.util.concurrent.TimeUnit
import scala.compiletime.uninitialized

import scala.reflect.ClassTag

@State(Scope.Thread)
@BenchmarkMode(Array(Mode.AverageTime))
@OutputTimeUnit(TimeUnit.NANOSECONDS)
class Map3Benchmark:

  @Param(Array("1", "4", "8", "16", "32", "64", "128", "256", "512", "1000", "10000"))
  var size: Int = uninitialized

  var array: Array[Int] = uninitialized

  @Setup
  def setup(): Unit = {
    System.gc()
    Thread.sleep(400) // чтобы GC успел пройти
    array = Array.fill(size)(1)
  }

  def heavy(x: Int): Int = Math.sqrt(x.toDouble).toInt
  def heavy2(x: Int): Int = Math.sqrt(2 * x.toDouble).toInt
  def heavy3(x: Int): Int = Math.sqrt(3 * x.toDouble).toInt

  @Benchmark
  def old_map_3(bh: Blackhole): Unit =
    bh.consume(
      array
        .oldMap(heavy)
        .oldMap(heavy2)
        .oldMap(heavy3)
    )

  @Benchmark
  def new_map_3(bh: Blackhole): Unit =
    bh.consume(
      array
        .newMap(heavy)
        .newMap(heavy2)
        .newMap(heavy3)
    )
