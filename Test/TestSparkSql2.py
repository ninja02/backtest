from pyspark import SparkConf,SparkContext
from pyspark.sql import HiveContext,StructField,StructType,IntegerType,StringType

conf = SparkConf().setAppName("spark_infer_schema")

sc = SparkContext(conf = conf)

hc = HiveContext(sc)

datas = ["1 a 28","2 b 29","3 c 30"]

source = sc.parallelize(datas)

splits = source.map(lambda line: line.split(" "))

rows = splits.map(lambda words: (int(words[0]),words[1],int(words[2])))



fields = []

fields.append(StructField("id",IntegerType().True))
fields.append(StructField("name",StringType().True))
fields.append(StructField("age",IntegerType().True))

schema = StructType(fields)

people = hc.applySchema(rows,schema)

people.registerTempTable("people")

results = hc.sql("select * from people where age>28 and age<30").collect()

sc.stop()

for result in results:
   print("id: %s, name: %s, age: %s" %(result.id, result.name, result.age))
   
   
   