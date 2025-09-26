import pandas as pd
import pandasql as ps
import sys

db_prefix = sys.argv[1]
print(db_prefix)

# Connecting Python to MySQL
import pymysql

def sql(query):
    return ps.sqldf(query)

connection = pymysql.connect(host ='dba-techday-1.czimjufijgjh.us-east-1.rds.amazonaws.com',port=int(3306),user='dbaadmin',passwd='bmcAdm1n')
cursor = connection.cursor()
cursor.execute(f'''use {db_prefix}_whiskey_retail_shop;''')

query = "TRUNCATE payments"
cursor.execute(query)
connection.commit()

columns_to_read = ['payment_id', 'date', 'customer_id', 'employee_id', 'product_id', 'price']
df = pd.read_csv("/mft_mountPath/payments.csv", usecols=columns_to_read)
# Drop columns that were added by Pandas
#df = df.drop(df.columns[[0]], axis=1)
records = [tuple(row) for row in df.to_numpy()]
query = "insert into payments (payment_id, date, customer_id, employee_id, product_id, price) values (%s, %s, %s, %s, %s, %s)"
cursor.executemany(query, records)

# Commit the transaction
connection.commit()