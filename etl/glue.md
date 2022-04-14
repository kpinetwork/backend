# Run Glue job script locally

Since we're using an ETL to proccess csv files to save new data in our db, we need to test the script locally to send it to Glue.


## Requirements
To run the script it is needed to have pyspark and all the dependencies for that.

- Java
- Scala
- Pyspark
- Jupyter
- Postgres
- Postgres JDBC driver

The following commands can be used on mac with homebrew


```
brew install openjdk@11
brew install scala
```

```
brew install apache-spark
```

```
pip install jupyter
```

You also need to [download](https://jdbc.postgresql.org/download.html) the postgres JDBC driver if you don't have it.

## Run script

To run script we need to set up pyspark to open with jupyter
```
export PYSPARK_DRIVER_PYTHON='jupyter'
export PYSPARK_DRIVER_PYTHON_OPTS='notebook'
```

And finally, it is needed to specify postgres driver location when pyspark is running
Replace *< path >* with the path for the driver and change the version of the driver (postgresql-42.3.3) if it is required.
```
pyspark --driver-class-path <path>/postgresql-42.3.3.jar
```

## Script

The [kpinetwork_analizer.py](kpinetwork_analizer.py) file constains some libraries and methods that only work on aws glue environment, to test the scrip locally it is necessary to change some of them

### Imports
Replace the imports with the following piece of code:

```
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.context import SparkContext
from pyspark.sql.functions import col
from pyspark.sql.types import DateType, StructType, StructField, StringType, BooleanType, DoubleType
import uuid
import datetime
import logging
import os
```

### Spark session
The script create a glueContext to save in the db the dataframes, however we don't use that, it is only required the spark session, for that write the following code:
```
sparkClassPath = os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.postgresql:postgresql:42.3.3 pyspark-shell'

spark = SparkSession.builder.config("spark.driver.extraClassPath", sparkClassPath).getOrCreate()
```

### Save to database function
Since aws glue resource has connections for our db it is not needed to add properties for the connection, so please change that function with this one:

```
def save_to_database(env, db_table, dataframe):
    database = ""
    
    logger.warning("Save in database")
    logger.warning("database: {} db_table: {}".format(database, db_table))
    url = "jdbc:postgresql://localhost/{}".format(database)
    properties = {
        "driver": "org.postgresql.Driver",
         "user": "",
         "password": ""
    }
    
    dataframe.write.jdbc(url=url, table=db_table, mode="append", properties=properties)
```
The values database, user and password should be added with your local database information

### Main function
Main function get the environment variables for the file path, however, we can pass directly the file_path of the CSV file to proccess

```
def main():
    env = 'demo'
    file_path = ''
    
    logger.warning(file_path)
    logger.warning("env: {}".format(env))

    proccess_file(file_path, env)
```

## Syntax details
In case you want to refactor the script, here are some details to be aware:

- Glue doesn't allow type hint, so if you add it in the script you'll get errors.
- Glue only show messages with logging warning

## Read more
- [Install pyspark on mac](https://sparkbyexamples.com/pyspark/how-to-install-pyspark-on-mac/)

- [Install pyspark on windows](https://sparkbyexamples.com/pyspark/how-to-install-and-run-pyspark-on-windows/)

- [Install Apache pyspark on windows](https://towardsdatascience.com/installing-apache-pyspark-on-windows-10-f5f0c506bea1)