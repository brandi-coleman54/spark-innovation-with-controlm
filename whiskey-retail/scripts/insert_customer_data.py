import pandas as pd
import pandasql as ps
import sys
import psycopg2
import os

pg_host = os.environ['POSTGRES_POSTGRESQL_SERVICE_HOST']
pg_password = os.environ['PG_PASSWORD']
db_prefix = sys.argv[1]

connection = psycopg2.connect(host=pg_host, port=int(5432), user='postgres',password=pg_password)
cursor = connection.cursor()
cursor.execute(f"SET search_path = {db_prefix}_whiskey_retail_shop;"

def sql(query):
    return ps.sqldf(query)

query = "TRUNCATE customers"
cursor.execute(query)
connection.commit()

columns_to_read = ['customer_id', 'first_name', 'last_name', 'full_name', 'email', 'street', 'four_digits', 'country_id', 'credit_provider_id']
df = pd.read_csv("/mft_mountPath/norm_customers.csv", usecols=columns_to_read)
# Drop columns that were added by Pandas
#df = df.drop(df.columns[[0,1]], axis=1)
records = [tuple(row) for row in df.to_numpy()]
query = "insert into customers (customer_id, first_name, last_name, full_name, email, street, four_digits, country_id, credit_provider_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
cursor.executemany(query, records)

    
# Commit the transaction
connection.commit()