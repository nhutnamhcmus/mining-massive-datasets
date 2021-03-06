# -*- coding: utf-8 -*-
"""CS246 - Colab 9.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/nhutnamhcmus/mining-massive-datasets/blob/main/CS246_Colab_9.ipynb

# CS246 - Colab 9
## Studying COVID-19

### Setup

Let's setup Spark on your Colab environment.  Run the cell below!
"""

!pip install pyspark
!pip install -U -q PyDrive
!apt install openjdk-8-jdk-headless -qq
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

"""Now we authenticate a Google Drive client to download the files we will be processing in our Spark job.

**Make sure to follow the interactive instructions.**
"""

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

# Authenticate and create the PyDrive client
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

id='1YT7ttUAafCjbVdm6obeHp1TWAK0rEtoR'
downloaded = drive.CreateFile({'id': id})
downloaded.GetContentFile('time_series_covid19_confirmed_global.csv')

id='1YxEA5UQ2EFJ_9oLssM__Gs1ncVNufGNA'
downloaded = drive.CreateFile({'id': id})
downloaded.GetContentFile('time_series_covid19_deaths_global.csv')

id='1CNxszuZTeIw-5cF5yrzKMZdb1qV0hSoy'
downloaded = drive.CreateFile({'id': id})
downloaded.GetContentFile('time_series_covid19_recovered_global.csv')

"""If you executed the cells above, you should be able to see the dataset we will use for this Colab under the "Files" tab on the left panel.

Next, we import some of the common libraries needed for our task.
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import pyspark
from pyspark.sql import *
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark import SparkContext, SparkConf

"""Let's initialize the Spark context."""

# create the session
conf = SparkConf().set("spark.ui.port", "4050")

# create the context
sc = pyspark.SparkContext(conf=conf)
spark = SparkSession.builder.getOrCreate()

"""You can easily check the current version and get the link of the web interface. In the Spark UI, you can monitor the progress of your job and debug the performance bottlenecks (if your Colab is running with a **local runtime**)."""

spark

"""If you are running this Colab on the Google hosted runtime, the cell below will create a *ngrok* tunnel which will allow you to still check the Spark UI."""

!wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
!unzip ngrok-stable-linux-amd64.zip
get_ipython().system_raw('./ngrok http 4050 &')
!curl -s http://localhost:4040/api/tunnels | python3 -c \
    "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])"

"""### Data Loading

In this Colab, we will be analyzing the timeseries data of the Coronavirus COVID-19 Global Cases, collected by Johns Hopkins CSSE.

Here you can check a realtime dashboard based on this dataset: [https://www.arcgis.com/apps/opsdashboard/index.html?fbclid=IwAR2hQKsEZ3D38wVtXGryUhP9CG0Z6MYbUM_boPEaV8FBe71wUvDPc65ZG78#/bda7594740fd40299423467b48e9ecf6](https://www.arcgis.com/apps/opsdashboard/index.html?fbclid=IwAR2hQKsEZ3D38wVtXGryUhP9CG0Z6MYbUM_boPEaV8FBe71wUvDPc65ZG78#/bda7594740fd40299423467b48e9ecf6)

---



*   ```confirmed```: dataframe containing the cumulative number of confirmed COVID-19 cases, divided by geographical area
*   ```deaths```: dataframe containing the cumulative number of deaths due to COVID-19, divided by geographical area
*   ```recovered```: dataframe containing the cumulative number of recoevered patients, divided by geographical area

The data sets contain data entries for each day, representing the cumulative totals as of that day.
"""

confirmed = spark.read.csv('time_series_covid19_confirmed_global.csv', header=True)
deaths = spark.read.csv('time_series_covid19_deaths_global.csv', header=True)
recovered = spark.read.csv('time_series_covid19_recovered_global.csv', header=True)

confirmed.printSchema()

confirmed.show()

deaths.show()

recovered.show()

"""### Your Task

We are aware of the stress we are all experiencing because of the still-ongoing pandemic and the fact that many of you have projects and exams due this week due to the lack of a finals week. As such, we decided to conclude our series of Colabs with a **lightweight task** -- given everything you have learned about Spark during the quarter, this Colab should take you just a few minutes to complete.

Consider the entries for May 1, 2021, in the timeseries, and compute:


*   number of confirmed COVID-19 cases across the globe
*   number of deaths due to COVID-19 (across the globe)
*   number of recovered patients across the globe
"""

# YOUR CODE HERE
number_of_confirmed = confirmed.agg({"5/1/21":"sum"}).collect()[0]["sum(5/1/21)"]
number_of_confirmed

number_of_deaths = deaths.agg({"5/1/21":"sum"}).collect()[0]["sum(5/1/21)"]
number_of_deaths

number_of_recovered = recovered.agg({"5/1/21":"sum"}).collect()[0]["sum(5/1/21)"]
number_of_recovered

"""Consider the data points for March 1, 2020, and March 1, 2021, and filter out the geographical locations where less than 50 cases have been confirmed.
For the areas still taken into consideration after the filtering step, compute the ratio between number of deaths and number of confirmed cases.
"""

# YOUR CODE HERE
query_confirmed = confirmed.select('Province/State', 'Country/Region', col('3/1/21').alias('confirmed(3/1/20)'))
query_deaths = deaths.select('Province/State', 'Country/Region', col('3/1/20').alias('deaths(3/1/20)'))
query_recovered = recovered.select('Province/State', 'Country/Region', col('3/1/20').alias('recovered(3/1/20)'))

df_march_1_2020 = query_confirmed.join(query_deaths, ['Province/State', 'Country/Region'])
df_march_1_2020 = df_march_1_2020.join(query_recovered, ['Province/State', 'Country/Region'])

df_march_1_2020 = df_march_1_2020.filter(df_march_1_2020['confirmed(3/1/20)'] >= 50)

df_march_1_2020 = df_march_1_2020.withColumn("recovered/confirmed", df_march_1_2020['recovered(3/1/20)'] / df_march_1_2020['confirmed(3/1/20)'])
df_march_1_2020 = df_march_1_2020.withColumn("deaths/confirmed", df_march_1_2020['deaths(3/1/20)'] / df_march_1_2020['confirmed(3/1/20)'])
df_march_1_2020.show()

query_confirmed = confirmed.select('Province/State', 'Country/Region', col('3/1/21').alias('confirmed(3/1/21)'))
query_deaths = deaths.select('Province/State', 'Country/Region', col('3/1/21').alias('deaths(3/1/21)'))
query_recovered = recovered.select('Province/State', 'Country/Region', col('3/1/21').alias('recovered(3/1/21)'))

df_march_1_2021 = query_confirmed.join(query_deaths, ['Province/State', 'Country/Region'])
df_march_1_2021 = df_march_1_2021.join(query_recovered, ['Province/State', 'Country/Region'])

df_march_1_2021 = df_march_1_2021.filter(df_march_1_2021['confirmed(3/1/21)'] >= 50)

df_march_1_2021 = df_march_1_2021.withColumn("recovered/confirmed", df_march_1_2021['recovered(3/1/21)'] / df_march_1_2021['confirmed(3/1/21)'])
df_march_1_2021 = df_march_1_2021.withColumn("deaths/confirmed", df_march_1_2021['deaths(3/1/21)'] / df_march_1_2021['confirmed(3/1/21)'])
df_march_1_2021.show()

"""Consider the data points for March 1, 2021, and May 1, 2021, in the timeseries, and filter out the geographical locations where less than 50 deaths have been confirmed (as of March 1, 2021).
For the areas still taken into consideration after the filtering step, compute the percent increase in cumulative deaths between the two dates.
"""

# YOUR CODE HERE
query_confirmed = confirmed.select('Province/State', 'Country/Region', col('5/1/21').alias('confirmed(5/1/21)'))
query_deaths = deaths.select('Province/State', 'Country/Region', col('5/1/21').alias('deaths(5/1/21)'))
query_recovered = recovered.select('Province/State', 'Country/Region', col('5/1/21').alias('recovered(5/1/21)'))

df_may_1_2021 = query_confirmed.join(query_deaths, ['Province/State', 'Country/Region'])
df_may_1_2021 = df_may_1_2021.join(query_recovered, ['Province/State', 'Country/Region'])

df_may_1_2021 = df_may_1_2021.filter(df_may_1_2021['confirmed(5/1/21)'] >= 50)

df_may_1_2021 = df_may_1_2021.withColumn("recovered/confirmed", df_may_1_2021['recovered(5/1/21)'] / df_may_1_2021['confirmed(5/1/21)'])
df_may_1_2021 = df_may_1_2021.withColumn("deaths/confirmed", df_may_1_2021['deaths(5/1/21)'] / df_may_1_2021['confirmed(5/1/21)'])


df_may_1_2021.show()

result = df_may_1_2021.join(df_march_1_2021, ['Province/State', 'Country/Region'])
result = result.withColumn("percent_increase", result["deaths(3/1/21)"] / result["deaths(5/1/21)"])
result.select(['Province/State', 'Country/Region', 'percent_increase']).show()

"""Once you have working code for each cell above, **head over to Gradescope, read carefully the questions, and submit your solution for this Colab**!"""