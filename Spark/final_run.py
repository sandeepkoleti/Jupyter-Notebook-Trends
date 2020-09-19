from __future__ import print_function
from pyspark.sql import SparkSession
from spark_processing import spark_processing
from pyspark.sql import SparkSession,SQLContext
from pyspark import SparkConf, SparkContext
from pyspark.sql import Row
import pyspark.sql.types as T


def main():
	
	"""
	Function calls to perform the final batch processing and writing 
	to the database.	
	
	"""
	
	
	parallel_processing = spark_processing()
	files_urls_df = parallel_processing.nb_repo_df()

	processed_df = parallel_processing.NotebookMapper(files_urls_df)
	processed_df.show()
	
	#df_lib.show()

	df_lib.write.format("jdbc") \
	    .option("url", "xxxx:5432/testing") \
	    .option("dbtable", "public.countlib") \
	    .option("user", "xxxx") \
	    .option("password", "xxxx") \
	    .option("driver","org.postgresql.Driver") \
	    .mode("append").save()

	#spark.catalog.clearCache()

if __name__ == "__main__":
  
  main()
