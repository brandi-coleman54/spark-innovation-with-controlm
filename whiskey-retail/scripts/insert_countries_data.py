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

#query = "TRUNCATE countries"
#cursor.execute(query)
#connection.commit()

columns_to_read = ['Country', 'Country_Code', 'country_id']
df = pd.read_csv("/mft_mountPath/countries.csv", usecols=columns_to_read)
# Drop columns that were added by Pandas
#df = df.drop(df.columns[[0]], axis=1)
records = [tuple(row) for row in df.to_numpy()]
query = "insert into countries (Country, Country_Code, country_id) values (%s, %s, %s)"
cursor.executemany(query, records)


# Commit the transaction
connection.commit()