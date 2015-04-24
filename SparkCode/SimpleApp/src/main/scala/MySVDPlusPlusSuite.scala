
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf

import org.apache.spark.graphx._

import com.github.fommil.netlib.BLAS.{getInstance => blas}

import org.apache.spark.rdd._

object MySVDPlusPlusSuite {

  def main(args: Array[String])  {
    val now = System.nanoTime
    val conf = new SparkConf().setAppName("Simple Application")
    val sc = new SparkContext(conf)
      val svdppErr = 8.0
      val edges = sc.textFile("/Users/Parry/Softwares-Big/spark-1.2.1-bin-hadoop2.4/examples/test/ratings.dat").map { line =>
        val fields = line.split("::")
        Edge(fields(0).toLong * 2, fields(1).toLong * 2 + 1, fields(2).toDouble)
      }
      val conf1 = new SVDPlusPlus.Conf(10, 100, 0.0, 5.0, 0.007, 0.007, 0.005, 0.015) // 2 iterations
      val (graph, _) = SVDPlusPlus.run(edges, conf1)
      graph.cache()
      val err = graph.vertices.map { case (vid, vd) =>
        if (vid % 2 == 1) vd._4 else 0.0
      }.reduce(_ + _) / graph.numEdges
      println("*****************")
      println(err)
      val microsec = (System.nanoTime - now)/1000
      println("Time taken = %d microseconds".format(microsec))
       }


}
