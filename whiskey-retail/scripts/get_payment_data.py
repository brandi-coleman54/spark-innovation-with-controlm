import numpy as np
import pandas as pd
import pandasql as ps
import random
from datetime import datetime


def sql(query):
    return ps.sqldf(query)

product_df = pd.read_csv("/mft_mountPath/products.csv")
product_id = product_df['product_id']
customer_df = pd.read_csv("/mft_mountPath/customers.csv")
customer_id = customer_df['customer_id']
employee_df = pd.read_csv("/mft_mountPath/employees.csv")
employee_id = employee_df['employee_id']

# Generating random days in the range of 1990 to 2020
date_range = pd.date_range(start = "2016-01-01", end = "2025-10-31", freq="D")

# Generating Unique payment id's
payment_id = np.random.default_rng().choice(999999, len(date_range), replace = False)

# Verify that there are as many ids as there are dates
assert len(set(payment_id)) == len(date_range)

# Verify that the new ids are unique
assert len(pd.Series(payment_id).unique()) == len(payment_id)

# Generating payments Data
customer_id_payments = []
employee_id_payments = []
product_id_payments = []
dates = []


# iterate through the payments and generate random data
for i in range(len(payment_id)):
    dates.append(datetime.strftime(random.choice(date_range), format='%Y-%m-%d'))
    customer_id_payments.append(random.choice(customer_id))
    employee_id_payments.append(random.choice(employee_id))
    product_id_payments.append(random.choice(product_id))
    
# Create a payments dataframe
payment_df = pd.DataFrame(payment_id, columns = ['payment_id'])
payment_df['date'] = sorted(dates)
payment_df['customer_id'] = customer_id_payments
payment_df['employee_id'] = employee_id_payments
payment_df['product_id'] = product_id_payments

# Adding the Alcohol_price column to the table
query = '''
select p1.*, p2.Alcohol_Price as price
from payment_df p1
inner join product_df p2
on p1.product_id = p2.product_id
'''

payment_df = sql(query)

payment_df.to_csv("/mft_mountPath/payments.csv")
