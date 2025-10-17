import pandas as pd
import pandasql as ps
import sys
import psycopg2
import os

pg_host = os.environ['POSTGRES_POSTGRESQL_SERVICE_HOST']
pg_password = os.environ['PG_PASSWORD']
db_prefix = sys.argv[1]

connection = psycopg2.connect(host=pg_host, port=int(5432), user='postgres',password=pg_password, database=f"{db_prefix}_whiskey_retail_shop")
cursor = connection.cursor()

def sql(query):
    return ps.sqldf(query)

columns_to_read = ['department_id', 'department']
df = pd.read_csv("/mft_mountPath/departments.csv", usecols=columns_to_read)
# Drop columns that were added by Pandas
#df = df.drop(df.columns[[0]], axis=1)
records = [tuple(row) for row in df.to_numpy()]
query = "insert into departments (department_id, department) values (%s, %s)"
cursor.executemany(query, records)


# Commit the transaction

connection.commit()
