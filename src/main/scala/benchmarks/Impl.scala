package benchmarks

import scala.reflect.ClassTag

extension [A](xs: Array[A]) {

  def oldMap[B](f: A => B)(implicit ct: ClassTag[B]): Array[B] = {
    val len = xs.length
    val ys = new Array[B](len)
    if (len > 0) {
      var i = 0
      (xs: Any @unchecked) match {
        case xs: Array[AnyRef]  => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Int]     => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Double]  => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Long]    => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Float]   => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Char]    => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Byte]    => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Short]   => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
        case xs: Array[Boolean] => while (i < len) { ys(i) = f(xs(i).asInstanceOf[A]); i = i + 1 }
      }
    }
    ys
  }

  def newMap[B](f: A => B)(implicit ct: ClassTag[B]): Array[B] = {
    val len = xs.length
    val ys = new Array[B](len)
    if (len > 0) {
      var i = 0
      while (i < len) {
        ys(i) = f(xs(i))
        i += 1
      }
    }
    ys
  }

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
