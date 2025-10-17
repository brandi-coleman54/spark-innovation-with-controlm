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

query = "TRUNCATE products"
cursor.execute(query)
connection.commit()

columns_to_read = ['Product_Name', 'Alcohol_Percent', 'Alcohol_Amount', 'Alcohol_Price', 'product_id']

product_df = pd.read_csv("/mft_mountPath/products.csv", usecols=columns_to_read)

records = [tuple(row) for row in product_df.to_numpy()]

query = "insert into products (Product_Name, Alcohol_Percent, Alcohol_Amount, Alcohol_Price, product_id) VALUES (%s, %s, %s, %s, %s)"
cursor.executemany(query, records)
    
# Commit the transaction

connection.commit()
