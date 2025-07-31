package benchmarks

import org.openjdk.jmh.annotations.*
import org.openjdk.jmh.infra.Blackhole
import java.util.concurrent.TimeUnit
import scala.compiletime.uninitialized

import scala.reflect.ClassTag

@State(Scope.Thread)
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

extension [A](xs: Array[A]) {

  def oldForeach[U](f: A => U): Unit = {
    val len = xs.length
    var i = 0
    (xs: Any @unchecked) match {
      case xs: Array[AnyRef]  => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Int]     => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Double]  => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Long]    => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Float]   => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Char]    => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Byte]    => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Short]   => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
      case xs: Array[Boolean] => while (i < len) { f(xs(i).asInstanceOf[A]); i = i + 1 }
    }
  }

  def newForeach[B](f: A => B)(implicit ct: ClassTag[B]): Unit = {
    val len = xs.length
    var i = 0
    while (i < len) {
      f(xs(i))
      i += 1
    }
  }

}
