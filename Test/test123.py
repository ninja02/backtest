from pyspark import SparkContext

logFile = "D:\spark\spark-1.6.0-bin-hadoop2.6\README.md"
sc = SparkContext("local","Simple App")
logData = sc.textFile(logFile).cache()

numAs = logData.count()

print("Lines with a: %i"%(numAs))