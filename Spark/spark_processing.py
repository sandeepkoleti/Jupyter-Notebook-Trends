import sys
import pyspark
from pyspark import SQLContext
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
import pyspark.sql.types as T
from pyspark.sql.functions import udf, expr, concat, col
from notebook_processing import ProcessNotebooks



class spark_processing(object):
	
	
	def __init__(self):
		self.spark = SparkSession \
		    .builder \
		    .appName("LibraryInsights") \
		    .getOrCreate()

		self.spark.sparkContext.addPyFile('notebook_processing.py')
		self.spark.sparkContext.addPyFile('timestamp.py')
		self.spark.sparkContext.addPyFile('import_lib.py')
		

	def nb_repo_df(self):
		
		"""
		Extract notebook ids and repository ids for each Jupyter Notebook

		"""
		
		df = self.spark.read.format("csv").option("header", "true").load("s3a://summarydatacsv/csv/notebooks.csv")
		df_selected_columns = df.select(df['nb_id'], df['repo_id'])
	
		return df_selected_columns


	def NotebookMapper(self,df_selected_columns):
		
		"""
		Distribute notebook ids to Spark workers
		Used flatmap to aggregrate users for each month for each library

		"""
		process_notebooks = ProcessNotebooks()

		lib_time_rdd = df_selected_columns.rdd.flatMap(process_notebooks.process_each_notebook) \
							.filter(lambda x: x[0][0] != 'lib_miss') \
							.reduceByKey(lambda n,m: n+m) \
							.map(lambda x: (x[0][0],x[0][1],x[1]))

	
		df_schema = StructType([StructField("libraries", StringType(), False),
						 StructField("timestamp", StringType(), False ),
						 StructField("counts", StringType(), False )])
	
		final_df = (
		    lib_time_rdd \
		    .map(lambda x: [x[0],x[1],x[2]]) \
		    .toDF(df_schema) \
		    .select("libraries","timestamp","counts")
		)

		
		return final_df


