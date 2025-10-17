import numpy as np
import pandas as pd
import sys, os
from datetime import datetime
import psycopg2
import psycopg2.extras

pg_host = os.environ['POSTGRES_POSTGRESQL_SERVICE_HOST']
pg_password = os.environ['PG_PASSWORD']
db_prefix = sys.argv[1]

connection = psycopg2.connect(host=pg_host, port=int(5432), user='postgres',password=pg_password, database=f"{db_prefix}_whiskey_retail_shop")
cursor = connection.cursor()

df = pd.read_csv("/mft_mountPath/all_dates.csv")
df = df.drop_duplicates()
# Drop columns that were added by Pandas
records = [tuple(row) for row in df.to_numpy()]
#query = "replace into dwh_date (Dates, Date_key, Day_name, Month_name, Year_name) values (%s, %s, %s, %s, %s)"
#cursor.executemany(query, records)
query = """
    INSERT INTO dwh_date (Dates, Date_key, Day_name, Month_name, Year_name)
    VALUES %s
    ON CONFLICT (Date_key) DO UPDATE
    SET
        Dates = EXCLUDED.Dates,
        Day_name = EXCLUDED.Day_name,
        Month_name = EXCLUDED.Month_name,
        Year_name = EXCLUDED.Year_name
"""
with connection.cursor() as cursor:
    # Use execute_values for efficient batch execution
    psycopg2.extras.execute_values(
        cursor,
        query,
        records,
        page_size=1000 # Optional, for performance tuning
    )
# Commit the transaction

connection.commit()
