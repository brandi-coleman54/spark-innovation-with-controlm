import numpy as np
import pandas as pd
import pandasql as ps

def sql(query):
    return ps.sqldf(query)

# Creating a new table called countries
customer_df = pd.read_csv("/mft_mountPath/customers.csv")
unique_countries = customer_df.country.unique()
countries_df = pd.DataFrame(unique_countries, columns = ['Country'])
countries_df['Country_Code'] = countries_df.Country.str[0:3]
countries_df['Country_Code'] = countries_df.Country_Code.str.upper()
countries_df['country_id'] = [*range(0,len(countries_df))]

# Extracting the country_id column from customers
query = '''
select countries_df.country_id
from customer_df 
join countries_df
on 
    customer_df.country_code = countries_df.country_code and
    customer_df.country = countries_df.country
'''
country_ids = sql(query)

# Connecting countries to customers by adding the foregin key: country_id
customer_df['country_id'] = country_ids

# Dropping the column country and country_code
customer_df = customer_df.drop(['country','country_code'],axis=1)

# Creating a new table called customer_cc
unique_cc_providers = customer_df.credit_provider.unique()
customer_cc_df = pd.DataFrame(unique_cc_providers, columns = ['credit_provider'])
customer_cc_df['credit_provider_id'] = [*range(0,len(customer_cc_df))]

# Extracting the credit_provider_id column from customers
query = '''
select customer_cc_df.credit_provider_id
from customer_df 
join customer_cc_df
on 
    customer_df.credit_provider = customer_cc_df.credit_provider
'''

credit_provider_id = sql(query)

# Connecting customer_cc to customers by adding the foregin key: credit_provider_id 
customer_df['credit_provider_id'] = credit_provider_id

# Dropping the column credit_provider
customer_df = customer_df.drop(['credit_provider'],axis=1)

customer_df.to_csv("/mft_mountPath/norm_customers.csv")
customer_cc_df.to_csv("/mft_mountPath/customer_cc.csv")
countries_df.to_csv("/mft_mountPath/countries.csv")
