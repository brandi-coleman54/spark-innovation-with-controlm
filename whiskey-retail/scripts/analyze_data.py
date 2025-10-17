import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import pandasql as ps
import streamlit as st
from empiricaldist import Pmf
import psycopg2
import os

pg_host = ${PG_CLUSTER_IP}
pg_password = ${PG_PASSWORD}
db_prefix = sys.argv[1]

connection = psycopg2.connect(host=pg_host, port=int(5432), user='postgres',password=pg_password)
cursor = connection.cursor()
cursor.execute(f"SET search_path = {db_prefix}_whiskey_retail_shop;")

plt.style.use('ggplot')
sns.set_palette('colorblind')
sns.set_context('notebook')

def pgsql(query, cursor):
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    df = pd.DataFrame(rows, columns=column_names)
    return df

def sql(query):
    return ps.sqldf(query)

#'''
#Pulling Data for Analysis
#'''
# Creating the query
query = f'''
select 
    f.date,
    d.Day_name as Day,
    d.Month_name as Month,
    d.Year_name as Year,
    f.Product_Name,
    f.Alcohol_Price,
    f.Alcohol_Percent,
    f.Alcohol_Amount,
    c.full_name as customer_name,
    co.country as customer_country,
    f.credit_provider,
    e.full_name as employee_name
from dwh_fact as f
left join {db_prefix}whiskey_retail_shop.customers c
on f.customer_id = c.customer_id
left join {db_prefix}whiskey_retail_shop.countries as co
on co.country_id = c.country_id 
left join dwh_employees as e
on e.employee_id = f.employee_id
left join dwh_date d
on d.Date_key = f.Date_key
order by f.date '''

# Generating a Dataframe according to the query
df = pgsql(query, cursor)
print(df)

#'''
#Pre-Processing
#'''
# Extracting a list of column
df_columns = df.columns.to_list()

# Iterating through the columns
for column in df_columns:
    
    # If the column is date, change the data type to datetime
    if column == 'date':
        df[column] = pd.to_datetime(df[column])
    
    # If the column is object, change the data type to category
    if df[column].dtype == 'object':
        df[column] = df[column].astype('category')
        
        
#'''
#Q1 — Which products produce the most profit?
#'''
# Generating a Dataframe containing the 5 most profitable products
query = '''
select 
    Product_Name,
    count(*) as Number_Of_Transactions, 
    sum(Alcohol_Price) as Profit
    
from df
group by Product_Name
order by sum(Alcohol_Price) desc
limit 5
'''

top_5_products = sql(query)

st.header("Top 5 Most Profitable")
st.dataframe(top_5_products, use_container_width=True)

sns.catplot(data = top_5_products, x = 'Product_Name', y = 'Profit', 
            kind = 'bar', palette='colorblind', height = 6, aspect = 2)
plt.xlabel('Product Name',size = 16)
plt.xlabel('Profit',size = 16)

plt.title('Top 5 Most Profitable Products',size = 18)
filename = '/opt/airflow/data/top5.png'
plt.savefig(filename)
#plt.show()
fp = open(filename, 'rb') 
img_data = fp.read()

#'''
#Q2 — Which products people usually buy?
#'''

query = '''
select 
    count(*) as Number_Of_Transactions, 
    Product_Name
    
from df
group by Product_Name
order by Number_Of_Transactions desc
limit 10
'''

most_bought_products = sql(query)
st.header("Most Purchased Products")
st.bar_chart(most_bought_products, y="Number_Of_Transactions", x="Product_Name")

# Generating a PMF
prob_mass_func = pd.DataFrame(Pmf.from_seq(df.Product_Name))

# Sorting 
sorted_prob_mass_func = prob_mass_func.iloc[:,0].sort_values(ascending = False)

# Filtering only the top 1 percentile of products
sorted_prob_mass_func = sorted_prob_mass_func[sorted_prob_mass_func > sorted_prob_mass_func.quantile(0.99)]

# Generating a Dataframe
probablity_Dataframe = pd.DataFrame()
probablity_Dataframe['Product'] = sorted_prob_mass_func.index
probablity_Dataframe['Probablity to Buy'] = sorted_prob_mass_func.values

# Output
#print(probablity_Dataframe)

#'''
#Q3 — Are there any interesting patterns as to when customers like to buy whiskey? If so what are they?
#'''
query = '''
select 
    count(*) as Number_Of_Transactions, 
    Month
    
from df
group by Month
order by count(*)
'''

most_bought_products_by_month = sql(query)

#print(most_bought_products_by_month)

sns.catplot(data = most_bought_products_by_month, 
            y = 'Number_Of_Transactions', x = 'Month', kind = 'bar',
           height = 6, aspect = 3, palette='colorblind')
plt.xlabel('Month', size = 18)
plt.ylabel('Number_Of_Transactions', size = 18)
plt.title('Number of Transaction vs Month', size = 22)
filename = '/opt/airflow/data/most_bought_by_month.png'
plt.savefig(filename)
#plt.show()

fp = open(filename, 'rb') 
img_data = fp.read()

#'''
#Q4 — Are we growing as a company in terms of profits or not?
#'''

query = '''
select 
    sum(Alcohol_Price) as Revenue, 
    year
    
from df
where year != 2022
group by year
order by year asc
'''

profits_by_year = sql(query)

#st.header("Revenue by Year")
#st.line_chart(profits_by_year, x="year", y="Revenue")

x = profits_by_year.Year
y = np.cumsum(profits_by_year.Revenue)

plt.rcParams["figure.figsize"] = [15, 8]
plt.rcParams["figure.autolayout"] = True
plt.plot(x,y)
plt.xlabel('Year', size = 16)
plt.ylabel('Profit(in Millions)', size = 16)
plt.title('Cummulative Profit', size = 20)
filename = '/opt/airflow/data/profits_by_year.png'
plt.savefig(filename)
#plt.show()

fp = open(filename, 'rb') 
img_data = fp.read()

#'''
#Q5 — From which counties do most of the customers come from
#'''
query = '''
select 
    count(distinct customer_name) as Number_of_customers, 
    customer_country
    
from df
group by customer_country
order by Number_of_customers desc
'''

customers_by_country = sql(query)

st.header("Customers by Country")
st.bar_chart(customers_by_country, y="customer_country", x="Number_of_customers")

customers_by_country['Number_of_customers'] = pd.to_numeric(customers_by_country['Number_of_customers'], errors='coerce')
# Filtering the top ten percentile of countries
customers_by_country = customers_by_country.sort_values(by = 'Number_of_customers', ascending=False)
topTenPc = int(len(customers_by_country.index)/10)
#print(f"topTenPc: {topTenPc}")
top_ten_percentile = customers_by_country.nlargest(topTenPc, 'Number_of_customers')

st.header("Top 10 Percentile")
st.dataframe(top_ten_percentile)

print(f"top_ten_percentile: {top_ten_percentile}")

sns.barplot(data =top_ten_percentile, x='Number_of_customers', y='customer_country', palette='colorblind')
filename = '/opt/airflow/data/customer_by_country.png'
plt.savefig(filename)
#plt.show()

fp = open(filename, 'rb') 
img_data = fp.read()

