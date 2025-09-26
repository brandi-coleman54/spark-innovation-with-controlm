import numpy as np
import pandas as pd
import sys, os
from datetime import datetime

db_prefix = sys.argv[1]
print(db_prefix)


# Connecting Python to MySQL
import pymysql

connection = pymysql.connect(host ='dba-techday-1.czimjufijgjh.us-east-1.rds.amazonaws.com',port=int(3306),user='dbaadmin',passwd='bmcAdm1n')
cursor = connection.cursor()
cursor.execute(f'''use {db_prefix}_whiskey_retail_shop;''')


df = pd.read_csv("/mft_mountPath/all_dates.csv")
df = df.drop_duplicates()
# Drop columns that were added by Pandas
records = [tuple(row) for row in df.to_numpy()]
query = "replace into dwh_date (Dates, Date_key, Day_name, Month_name, Year_name) values (%s, %s, %s, %s, %s)"
cursor.executemany(query, records)

# Commit the transaction
connection.commit()