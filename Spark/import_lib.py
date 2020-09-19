import json
import boto3
import botocore
import datetime
import os
import pyspark
from pyspark.sql import SparkSession,SQLContext
from pyspark import SparkConf, SparkContext


class GetImportedLibraries():

        def get_libraries(self,nb_id,s3_res):

		"""
		Function to extract imported libraries from each notebook

		"""

		notebook_path = "s3a://notebooksdata/nb_"+nb_id+".ipynb"
		key = str(notebook_path)[20:]
		file_name = "nb_"+nb_id+".ipynb"

                importedItems = []
		
		#Exception to handle missing file from the dataset
                try:
                        s3_res.Bucket('notebooksdata').download_file(key,file_name)
                except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                                return []

                try:
                        with open(file_name, 'r') as filedata:
                                data1 = filedata.read()
                        data = json.loads(data1)

                except ValueError:
                        return []

                total_length = []


                if isinstance(data, dict):
                        cell_keys = data.keys()
                cell_keys = data.keys()
                                                     

		if 'cells' in cell_keys:
                        for c in data['cells']:
                                #print(c)
                                cell_data = self.get_lib_data(c,total_length)
                                for i in cell_data:
                                        importedItems.append(i)

                return list(set(importedItems))



        def get_lib_data(self,cell,total_length):

                if isinstance(cell, dict):
                        cell_keys = cell.keys()
                else:
                        cell_keys = []

                if 'cell_type' in cell_keys:
                        cell_type = cell['cell_type']
                else:
                        cell_type = None
		
		#Accessing only the code cells and thereby the source cells having the actual code
                if cell_type == 'code':
                        lines_of_code = []
                        if 'source' in cell_keys:
                                if isinstance(cell['source'], list):
                                        if cell['source'] == []:
                                                pass
                                        else:
                                                lines_of_code = cell['source'][0].partition("#")[0].partition("as")[0].split(' ')
                                        
                                elif isinstance(cell['source'], str):
                                        lines_of_code = cell['source'].split('  ')
                                        #print(lines_of_code)
                        elif 'input' in cell_keys:
                                if isinstance(cell['input'], list):
                                        if cell['input'] == []:
                                                pass
                                        else:
                                                lines_of_code = cell['input'][0].partition("#")[0].partition("as")[0].split(' ')
                                elif isinstance(cell['input'], str):
                                        lines_of_code = cell['input'].split(' ')

                        #print(lines_of_code)
                        total_length.append(lines_of_code)

                return total_length


