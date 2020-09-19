import json
import datetime
import boto3
import botocore
class GetTimeStamps(object):

	def get_time_stamps(self,repo_id,s3_resource):
		
		"""

		Given repository metadata for each notebook, returns a formatted date-timestamp
		considering the 'updated at:' key in the json files

		"""

		repo_path = "s3a://repojsondata/repo_"+repo_id+".json"
		key = str(repo_path)[19:]
		file_name = "repo_"+repo_id+".json"

		# Handling exceptions in case of missing files
		try:
			s3_resource.Bucket('repojsondata').download_file(key,file_name)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				return 'none'
	
		s3_resource.Bucket('repojsondata').download_file(key,file_name)
		
		
		try:
			
			with open(file_name, 'r') as file_data:
				data = file_data.read()
			json_data = json.loads(data)
			
			if 'updated_at' in json_data:
				timestamp = str(json_data['updated_at'])
				timestamp = str(timestamp)
				date_time = datetime.datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%SZ')
				formatted_timestamp = "%Y-%m"
				final_date = date_time.strftime(formatted_timestamp)
				return final_date
			else:
				return 'none'
		except:
			pass
  





