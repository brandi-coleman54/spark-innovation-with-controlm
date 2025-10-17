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

query = "TRUNCATE employees"
cursor.execute(query)
connection.commit()

columns_to_read = ['employee_id', 'first_name', 'last_name', 'full_name', 'email', 'city', 'department_id']
df = pd.read_csv("/mft_mountPath/norm_employees.csv", usecols=columns_to_read)
# Drop columns that were added by Pandas
#df = df.drop(df.columns[[0,1]], axis=1)
records = [tuple(row) for row in df.to_numpy()]
query = "insert into employees (employee_id, first_name, last_name, full_name, email, city, department_id) values (%s, %s, %s, %s, %s, %s, %s)"
cursor.executemany(query, records)

    
# Commit the transaction

connection.commit()
