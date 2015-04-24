name := "MRS"

version := "1.0"

scalaVersion := "2.10.4"

libraryDependencies += "org.apache.spark" %% "spark-core" % "1.2.1" % "provided"

libraryDependencies += "org.apache.spark" %% "spark-graphx" % "1.2.1" % "provided"

libraryDependencies += "org.apache.spark"  % "spark-mllib_2.10" % "1.2.1" % "provided"

libraryDependencies += "com.github.scopt" %% "scopt" % "3.3.0" 

resolvers += Resolver.sonatypeRepo("public")