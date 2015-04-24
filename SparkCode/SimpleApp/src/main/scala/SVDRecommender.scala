

import org.apache.spark.mllib.linalg.Matrix
import org.apache.spark.mllib.linalg.distributed.RowMatrix
import org.apache.spark.mllib.linalg.SingularValueDecomposition
import org.apache.spark.rdd.RDD
import org.apache.spark.mllib.linalg.{Vector, Vectors}
import org.apache.spark.mllib.linalg._
import org.apache.spark.{SparkConf, SparkContext}
import scala.math
import org.apache.spark.SparkContext._
import math._
import java.util.Arrays
import org.apache.spark.mllib.linalg.distributed.IndexedRowMatrix
import org.apache.spark.mllib.linalg.distributed.IndexedRow
 
object SVDRecommender
{
  def main(args: Array[String]): Unit = 
  {
      val now = System.nanoTime
        val conf = new SparkConf().setAppName("SVD Recommender")
        conf.setMaster("local[2]")      
        val sc = new SparkContext(conf) // spark context tells spark how to access a cluster
        
 /*------------------------------- step 1: data representation ----------------------------------  */    
        //input data will contain the ratings in the form of tuples (userID, itemID, rating)
        val inputData = sc.textFile("/Users/Parry/Softwares-Big/spark-1.2.1-bin-hadoop2.4/examples/test/ratings.dat")
        .map{ line => val parts = line.split("::")
    (parts(0).toLong, parts(1).toInt, parts(2).toDouble) //split each line of input into 3 parts: uID, itemID and rating
          }   
        //dividing the data set into training set and test set
        val splits= inputData.randomSplit(Array(0.35, 0.65), seed=11L)
        var training = splits(0).cache
        val test= splits(1).cache
        // test.foreach(a => {println("Test&##########################################################")
        //    println(a)})
        // training.foreach(a => {println("Training&##########################################################")
        //    println(a)})
        //Ensuring to have all the users in the matrix  
        val usersNotInTraining= test.map(_._1).subtract(training.map(_._1))
        training= training.union( usersNotInTraining.map(u => (u, 1, 0)))
           
        // Number of columns which is equal to number of items. These columns will have indices starting from 0 to nCol-1
        val nCol = inputData.map(_._2).max()
        println("&##########################################################")
        println("nCol:" + nCol )
        
        //Construct rows of the IndexedRowMatrix R
        val dataRows = training.groupBy(_._1).map[IndexedRow]{ row =>   //groubBy userID
      
        val (indices, values) = row._2.map(e => (e._2, e._3)).unzip//unzip will collect the 1st element of all the tuple in a list and similarly for the 2nd elements in the tuples    
        val ind = indices.toArray //hold column indices
        val v= values.toArray
        
        v.foreach(a => println(a))
        var userRow= new Array[Double](nCol) //this is initialized by zeros. It will hold the preferences of 1 user
        for (i <- 0 to ind.length-1){ //this is similar to uRow.update (index, value)            
          userRow.update(ind(i)-1, v(i))  //uRow(ind(i)-1) = v(i)
        }
        IndexedRow (row._1, Vectors.dense(userRow)) //return an indexedRow storing the user preferences
        }
        
        val ratingsMatrix = new IndexedRowMatrix(dataRows.persist()) //persist keeps the data in memory so that it could be shared among queries. It stores user-item matrix
     
/*------------------------------- step 2: preprocessing ----------------------------------  */       
        val matrixStat = ratingsMatrix.toRowMatrix.computeColumnSummaryStatistics
        val colSum= matrixStat.mean.toArray.map(_ * (ratingsMatrix.numRows-1))  //finding the sum of each column. mean is computed by adding all the value of the row even the zeros
     
        val colMean= colSum.zip(matrixStat.numNonzeros.toArray).map{t=>  t._2 match { case 0 => 0; case _ => t._1 / t._2 } } //finding the mean of non-zero values only : (colSum / numNonZeroIntheCorrespondingColumn)
   
        //computing the mean of each row; i.e. average ratings for each user
        val rowsMean = ratingsMatrix.rows.map{r => 
        val s = r.vector.toArray.sum 
        var nonZeroCount= r.vector.toArray.count( v => v != 0 )
        if(nonZeroCount ==0 ){
        nonZeroCount = 1
        }
      
            val rMean = s/(nonZeroCount)
            (r.index ,rMean)
       
         }.cache.collect.toMap
         
        // fill unknown entries (holding zero) by the average of colMean and rowMean
        //t._1 is the rating or 0 for unknown ratings while t._2 is the mean of the corresponding column
        // rating + ((1-ceil(raiting/max rate)) * movieMean) 
        // don't change known ratings. Thus, ratings + (0 * movieMean)
        //for unknown ratings: 0 +( (1- 0) * movieMean))
        val filledRDD= ratingsMatrix.rows.map{ r =>

          val rowMean= rowsMean(r.index) 
        IndexedRow (r.index, Vectors.dense( r.vector.toArray.zip(colMean).map(t => t._1+ ((1-math.ceil(t._1/5.0))* ((t._2+rowMean)/2)) ) )) }
 
         
        //Normalize the resulting Matrix by subtracting customer average from each row
         val normalizedRDD= filledRDD.map{r => 
         val mean= rowsMean(r.index) 
         // println(r.index)
         // println(mean)
         IndexedRow (r.index, Vectors.dense(r.vector.toArray.map(e => e - mean)/* end of map*/   ) /*end of Vectors*/)/*end of indexedRow*/
         }/*end of map*/
         
/*------------------------------- step 3: Computing SVD ----------------------------------  */           
        // Compute k largest singular values and corresponding singular vectors
        val k = 20
        
        val normalizedMatrix = new IndexedRowMatrix(normalizedRDD)
        // println(normalizedMatrix)
        val svd= normalizedMatrix.computeSVD(k, computeU = true)
                 
/*---------------------------------- step 4: Computing the predictions ------------------------------*/
        //construct S matrix
        var sArray= new Array[Double](k*k) //this is initialized by zeros
        for (i <-0 to  k-1) //filling the diagonal entries by the singular values
        {
          sArray((k+1)*i)= svd.s.toArray(i)
        }          
        
        //multiply U and S
        val US = svd.U.multiply(Matrices.dense(k, k, sArray))
         
       //multiply US and VË†t 
        val arr = svd.V.toArray.grouped(svd.V.numRows).toList.transpose.toArray // This holds vt column by column
        //Note: svd.v.toArray will hold V column by column which is equivalent to the transpose. And since we want to save this transpose column by column, we need to convert it to Array again
        
        val vtarr = arr.reduce(_++_)//concatenate the columns of vt
        val vt= Matrices.dense(k, nCol, vtarr.toArray) 
                    
        val prediction = US.multiply(vt)
       
         val denormalizedPredictions= prediction.rows.map{r => 
         val mean= rowsMean(r.index) 
         IndexedRow (r.index, Vectors.dense(r.vector.toArray.map(e => e + mean)/* end of map*/   ) /*end of Vectors*/)/*end of indexedRow*/
         }/*end of map*/
         
/*------------------------------- step 5: Evaluating SVD-Based Recommender ----------------------------------  */     
        //computing the AME between test data set and the computed normalized predictions
        //1) change the format of the test data in order to join it with the predictions and then find the error between them   
        val testSet = test.map ( t => ((t._1, t._2), t._3))
        val uIdAndPref= denormalizedPredictions.flatMap{ case r => 
        r.vector.toArray.zipWithIndex.map{ case e =>   
        ((r.index, e._2 + 1), e._1)} }
        
        val  testAndPref = testSet.join(uIdAndPref)
        
        val meanÙAbsErr= testAndPref.map{case ((uId, iID), (r1 ,r2)) => val er = (r1-r2)
        Math.abs(er)   
       }.mean
 
        println("M A E " + meanÙAbsErr)
       val microsec = (System.nanoTime - now)/1000
      println("Time taken = %d microseconds".format(microsec))
       //clean up and shut down the context
        sc.stop()

  }
}