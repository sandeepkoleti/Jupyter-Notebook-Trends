# Jupyter Trends

A data pipeline tool to analyze most popular libraries actively used in publicly available Jupyter Notebooks on Github and thereby recommend popular Github users who follow code modularity as well as have sufficient hands-on experience in these popular libraries.



## Overview
We are often spoilt for choices and so is a programmer looking for solution on various platforms like Stackoverflow, Medium, Stackexchange only to understand the superficial functionality of the solution! 
Many developers are often in search of understanding a practical approach for using various trending tools and libraries along with a clean and modular code base approach!
Github is a great resource for such coders to learn what’s trending and what good coding practices are!
In order to make this enthusiastic users base practicing code modularity accessible to everyone, I am  building on project which aggregated popular libraries used in Jupyter Notebooks to also add information on modularity of notebooks! This way new coders can see good examples of modular coding practice 

**My project is an attempt to shorten the searching space by processing 1.25 million Jupyter Notebooks to identify and recommend top github users having experience in these trending libraries who actually follow modular way of writing code!**

This tool also serves a dual purpose as recruiters can consider these recommended Github users as their potential future employees! 

**Dataset -** The dataset is a combination of 1.25 million Jupyter Notebooks, notebook metadata json files and .csv files for summarizing and indexing the above files. The dataset was published by Design Lab at UC San Diego in July 2017.

[Dataset Link](https://library.ucsd.edu/dc/object/bb2733859v)

## Pipeline
![Pipeline](https://github.com/pjm526/Jupyter-Trends/blob/master/Figures/pipeline.png)

## Requirements
* Python3
* [AWS CLI](https://aws.amazon.com/cli/)
* [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#installation)

## Architecture
* [SPARK](https://blog.insightdatascience.com/simply-install-spark-cluster-mode-341843a52b88): 4 EC2 m4.large instances with (1 master 3 worker) spark cluster
* [POSTGRESQL](https://blog.insightdatascience.com/simply-install-postgresql-58c1e4ebf252): 1 EC2 m4.large instance
* [DASH](https://dash.plot.ly/installation): 1 EC2 t2.micro instance 

## Methodology

### Data Collection:
Parse and extract the urls available on UC San Diego Library Digital Collections into s3 buckets buy distributing the work among worker nodes as well.
Lambda Fucntion to unzip the zipped files inot ec2 instance and then write it to the s3 bucket using `s3.put_object()`
Loaded repository metadata to extract 'updated at:' timestamp.
Extracted notebooks ids, repository ids, github user names from the csv files and hence mapped the results to respective tables. 


### Extracting Libraries from Notebooks
Load the .ipynb notebooks which are in json format as dictionaries to make use of dictionary look up functions to access the source cells from the notebooks.Using regex functions look for keywords "import" and "from" to retrieve the libraries.

Extract timestamps from the repository metadata json files and attach it to each libraries.

Using RDD's calculate the count for each tuple crated above to get the total count.
Stored the final spark dataframe in PostgreSQL by setting up the connections.
 
 ### Calculating Code Modularity Metrics
 I considered the following metrics to calculate how modular a notebook is:
 * Functions: Calculated the number of times keyword **def** occured in a notebook in source cells.
 * Classes: Calculated the number of times keyword **class** occured in a notebook in source cells.
 * Comments: Calculated the number of times **"#"** and **" """ "** occured in a notebook in source cells.
 * Lines of Code: Stripped the lines in source cells on (\n) and subtracted the number of comments from the total lines of code to get actual lines count.
 
 Stored the final spark dataframe in PostgreSQL by setting up the connections.
 
 ## Dashboard
 ![Dynamic Dashboard](https://github.com/pjm526/Jupyter-Trends/blob/master/Figures/Screenshot%20from%202020-02-13%2011-57-33.png)
 
 ## Deployment
 
 Calculate libraries, timestamp and total count
 
 `nohup spark-submit --class etl --num-executors 3 --executor-cores 6 --executor-memory 6G --master spark://ec2-52-204-48-171.compute-1.amazonaws.com:7077 --packages org.postgresql:postgresql:42.2.9 --jars /usr/local/spark/jars/postgresql-42.2.9.jar final_run.py &`

Calculate Code Modularity Metrics

`nohup spark-submit --class etl --num-executors 3 --executor-cores 6 --executor-memory 6G --master spark://ec2-52-204-48-171.compute-1.amazonaws.com:7077 --packages org.postgresql:postgresql:42.2.9 --jars /usr/local/spark/jars/postgresql-42.2.9.jar notebook_metrics.py &`

Deploying Frontend

`sudo python3 frontend.py`
 

