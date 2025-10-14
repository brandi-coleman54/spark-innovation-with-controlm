import numpy as np
import pandas as pd
import sys, os
from datetime import datetime
import psycopg2

pg_host = os.environ['POSTGRES_POSTGRESQL_SERVICE_HOST']
pg_password = os.environ['PG_PASSWORD']
db_prefix = sys.argv[1]

connection = psycopg2.connect(host=pg_host, port=int(5432), user='postgres',password=pg_password)
cursor = connection.cursor()
cursor.execute(f"SET search_path = {db_prefix}_whiskey_retail_shop;"


df = pd.read_csv("/mft_mountPath/all_dates.csv")
df = df.drop_duplicates()
# Drop columns that were added by Pandas
records = [tuple(row) for row in df.to_numpy()]
query = "replace into dwh_date (Dates, Date_key, Day_name, Month_name, Year_name) values (%s, %s, %s, %s, %s)"
cursor.executemany(query, records)

# Commit the transaction
connection.commit()