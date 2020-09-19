import boto3
import json
import pyspark
import os
import subprocess
from pyspark.sql import SparkSession,SQLContext
from pyspark import SparkConf, SparkContext
from pyspark.sql import Row
from itertools import chain
from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
import pyspark.sql.types as T
from spark_processing import spark_processing
from notebook_processing import ProcessNotebooks

count = 0

def code_modularity(df):

	"""
	Calculate the number of functions, classes, lines of codes and comments in a jupyter notebook.

	"""
        nb_id = df.nb_id
        s3_resource = boto3.resource('s3')
        repo_path = "s3a://notebooksdata/nb_"+nb_id+".ipynb"
        key = str(repo_path)[20:]
        #print(key)
        fileName = "nb_"+ nb_id+ ".ipynb"
        s3_resource.Bucket('notebooksdata').download_file(key,fileName)

        all_cells = []
        func_count = 0
        lib_count = 0
        comments = 0
        final_score = 0
        total_length = []

        global count
        count += 1
                                                                          
	try:
		#Loading file as a dictionary            
		with open(fileName, 'r') as filedata:
                        data1 = filedata.read()
                data = json.loads(data1)

        except ValueError:
                #return final_score
                return (nb_id,0,0,0,0)
      
        if isinstance(data, dict):
                cell_keys = data.keys()
        cell_keys = data.keys()

        if 'cells' in cell_keys:
                for c in data['cells']:
                        #print(c)
                        cell_data = get_cell_data(c,total_length)
                        all_cells.append(cell_data)

        for i in range(len(all_cells)):
                func_count += all_cells[i][0]
                lib_count += all_cells[i][1]
                comments += all_cells[i][2]

	#Getting rid of the notebooks loaded in memory
        if count == 1000:
                print("Inside the count")
                os.system("rm *.ipynb")
                count = 0

	lines_of_code = len(total_length) - comments
        return (nb_id,func_count, lib_count, comments, lines_of_code)
     

def get_cell_data(cell,total_length):
	
	"""
	Calculating the metrics for each cell
	"""

        if isinstance(cell, dict):
                cell_keys = cell.keys()
        else:
                cell_keys = []

        if 'cell_type' in cell_keys:
                cell_type = cell['cell_type']
        else:
                cell_type = None

        comments = 0
        func_count = []
        class_count = []
        in_multiline = False

        if cell_type == 'code':
                
                lines_of_code = []
                if 'source' in cell_keys:
                        if isinstance(cell['source'], list):
                                lines_of_code = cell['source']
                        elif isinstance(cell['source'], str):
                                lines_of_code = cell['source'].splitlines()
                elif 'input' in cell_keys:
                        if isinstance(cell['input'], list):
                                lines_of_code = cell['input']
                        elif isinstance(cell['input'], str):
                                lines_of_code = cell['input'].splitlines()
		total_length.append(i for i in lines_of_code)

                for i in lines_of_code:
                        total_length.append(i)

                for l in lines_of_code:
                        l = l.lstrip()
                        parts = l.split()
                        if len(parts) >= 2:'

				#Function count calculation
                                if l.startswith('def'):
                                        #print("inside")
                                        func_count.append(parts[1].split('(')[0])
                                        
				#Class count calculation
                                elif l.startswith('class'):
                                        class_count.append(parts[1].split('(')[0])

			#Comment count calculations
                        if in_multiline:
                                comments += 1

                        if l.startswith('"""'):
                                if not in_multiline:
                                        comments += 1
                                in_multiline = not in_multiline

                        elif l.startswith("'''"):
                                if not in_multiline:
                                        comments += 1
                                in_multiline = not in_multiline

                        elif l.startswith('#'):
                                comments += 1

        return [len(func_count), len(class_count), comments]


def main():

	conf = SparkConf().setAppName("JupyterTrends")
	sc = SparkContext(conf=conf)

	spark = SparkSession \
		    .builder \
		    .appName("LibraryInsights") \
		    .getOrCreate()
	spark.conf.set("spark.sql.crossJoin.enabled", "true")

	bucketName = "notebooksdata"
	#prefix = 'sample_data/data/notebooks/'
	s3 = boto3.client('s3')
	s3_data = s3.list_objects_v2(Bucket=bucketName)
	s3_resource = boto3.resource('s3')

	if 'Contents' not in s3_data:
		print("None")

	#To get the list of all jupyter notebook files names
	fileList = []
	for key in s3_data['Contents']:
		fileList.append("s3a://" + bucketName + "/" + key['Key'])
	print("List count = " + str(len(fileList)))


	while s3_data['IsTruncated']:
		continuation_key = s3_data['NextContinuationToken']
		s3_data = s3.list_objects_v2(Bucket='notebooksdata', ContinuationToken=continuation_key)
		if 'Contents' not in s3_data:
		        break
		else:
		        file_list_1000 = []
		        for key in s3_data['Contents']:
		                file_list_1000.append("s3a://notebooksdata/" + key['Key'])
		        fileList.extend(file_list_1000)
		        print("List count = " + str(len(fileList)))

	notebook_id_list = []
	for fileName in fileList:
		file_path = fileName.encode("utf-8")
		#print(file_path)
		# strip off the starting s3a:// from the bucket
		current_bucket = os.path.dirname(str(file_path))[6:18]
		# strip off the starting s3a://<bucket_name>/ the file path
		key = str(file_path)[20:]
		file_name = os.path.basename(str(file_path))
		notebook_id = os.path.splitext(file_name)[0][3:]
		notebook_id_list.append(notebook_id)


	rdd1 = sc.parallelize(notebook_id_list)
	row_rdd = rdd1.map(lambda x: Row(x))
	df = spark.createDataFrame(row_rdd,['nb_id'])
	df.show()

	#Distribute jupyter notebooks to Spark workers to calculate modularity metrics
	score_rdd= df.rdd.map(code_modularity).map(lambda x: (x[0],x[1],x[2],x[3],x[4]))
	score_list = score_rdd.collect()

	#Dataframe to store the calculated results
	schema = T.StructType([StructField("nb_id",T.StringType(),False),
		             StructField("func_count", T.LongType(),False),
		        StructField("class_count", T.LongType(),False),
		        StructField("comment_count", T.LongType(),False),
		        StructField("lines_of_code", T.LongType(),False)])

	#rdd_list= sc.parallelize(map(list, rdd_final.collect()))
	score_df = spark.createDataFrame(score_list,schema)
	#score_df.show()

	get_df = spark.read.format("csv").option("header", "true").load("s3a://summarydatacsv/csv/notebooks.csv")
	df = get_df.select(get_df['nb_id'], get_df['repo_id'])

	##Join to get owner_login information 
	merge_df = spark.read.format("csv").option("header", "true").load("s3a://summarydatacsv/csv/repositories.csv")
	merge_df = merge_df.select(merge_df['repo_id'], merge_df['owner_login'])
	df = df.join(merge_df,df['repo_id'] == merge_df['repo_id']).drop(merge_df['repo_id'])
	df = df.join(score_df, df['nb_id'] == score_df['nb_id']).drop(df['nb_id'])


	#Store the final dataframe in PostgreSQL
	df.write.format("jdbc") \
	    .option("url", "jdbc:xxxx:5432/testing") \
	    .option("dbtable", "public.finalscores") \
	    .option("user", xxxx) \
	    .option("password", xxxx) \
	    .option("driver","org.postgresql.Driver") \
	    .mode("append").save()

if __name__ == "__main__":
	main()

                                                                              
