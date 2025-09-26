import pandas as pd
import pandasql as ps
import sys

db_prefix = sys.argv[1]
print(db_prefix)

# Connecting Python to MySQL
import pymysql

connection = pymysql.connect(host ='dba-techday-1.czimjufijgjh.us-east-1.rds.amazonaws.com',port=int(3306),user='dbaadmin',passwd='bmcAdm1n')
cursor = connection.cursor()
cursor.execute(f'''use {db_prefix}_whiskey_retail_shop;''')

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