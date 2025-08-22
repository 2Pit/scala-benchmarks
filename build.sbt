import sbt._
import Keys._

// версии компилятора
val scala2 = "2.13.14"
val scala3 = "3.7.1"

// глобально (можно и внутри проекта, но так удобнее)
ThisBuild / scalaVersion := scala2
ThisBuild / crossScalaVersions := Seq(scala2, scala3)

lazy val root = (project in file("."))
  .enablePlugins(JmhPlugin)
  .settings(
    name := "speedup-array",
    version := "0.1.0-SNAPSHOT",
    // libraryDependencies += "org.scalameta" %% "munit" % "1.0.0" % Test,

    // JIT-логирование для процессов JMH
    // Если вдруг sbt ругается на Jmh, добавь: import pl.project13.scala.sbt.JmhPlugin.autoImport._
    Jmh / javaOptions ++= {
      val dir = (Jmh / target).value / "jit-logs"
      IO.createDirectory(dir)
      val log = dir / s"jit-${scalaVersion.value}-%p-%t.log"
      Seq(
        "-XX:+UnlockDiagnosticVMOptions",
        // "-XX:+PrintCompilation",
        // "-XX:+PrintInlining",
        "-XX:+LogCompilation",
        s"-XX:LogFile=${log.getAbsolutePath}"
      )
    }
  )
