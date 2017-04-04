from pyspark import SparkConf,SparkContext
from pyspark.sql import HiveContext,Row

conf = SparkConf().setAppName("spark_infer_schema")

sc = SparkContext(conf = conf)

hc = HiveContext(sc)

datas = ["1 a 28","2 b 29","3 c 30"]

source = sc.parallelize(datas)

splits = source.map(lambda line: line.split(" "))

rows = splits.map(lambda words: Row(id = words[0],name = words[1],age=words[2]))

people = hc.inferSchema(rows)

people.printSchema()

people.registerTempTable("people")

results = hc.sql("select * from people where age>28 and age<30")

results.printSchema()

results.registerTempTable("people2")

results2 = hc.sql("select name from people2")

results2.printSchema()

results3 = results2.map(lambda row: row.name.upper()).collect()

for result in results3:
    print("name:"+result)

sc.stop()