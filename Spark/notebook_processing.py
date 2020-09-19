import sys
import os
import pyspark
import boto3
#import pandas as pd
from timestamp import GetTimeStamps
from import_lib import GetImportedLibraries



class ProcessNotebooks(object):

	def process_each_notebook(self, file_info):

			
		s3_resource = boto3.resource('s3')
		total_data = []

        	# Extract timestamp for each jupyter notebook
		get_timestamp = GetTimeStamps()
		year_month_date = get_timestamp.get_time_stamps(str(file_info.repo_id), s3_resource)
		if year_month_date == 'none':
			total_data.append((('lib_miss','date_miss'),0))
			return total_data

        	# Extract all imported libraries for each jupyter notebook
		lib = GetImportedLibraries()
		libraries_imported = lib.get_libraries(str(file_info.nb_id),s3_resource)

		# Tuple formation to perform reduceBy later
		if libraries_imported != None:
			for library in libraries_imported:
				total_data.append(((library,year_month_date),1))
		else:
			return 	
	
		return total_data



