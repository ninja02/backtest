from pyspark import SparkConf,SparkContext
from pyspark.sql import HiveContext,Row

conf = SparkConf().setAppName("spark_infer_schema")

sc = SparkContext(conf = conf)

hc = HiveContext(sc)

datas = ["baidu 202.108.22.5","sina 202.108.33.32"]

source = sc.parallelize(datas)

splits = source.map(lambda line: line.split(" "))

rows = splits.map(lambda words: Row(company=words[0], ip=words[1]))

messages = hc.inferSchema(rows)

messages.registerTempTable("messages")

def change(company):
    return company.upper()

hc.registerFunction("mychange",change)

results = hc.sql("select mychange(company), func.iptolocationbysina(ip) from messages").collect()

sc.stop()

for result in results:
    print(result)
