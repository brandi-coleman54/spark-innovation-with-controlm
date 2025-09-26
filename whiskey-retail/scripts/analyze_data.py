import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import pandasql as ps
from empiricaldist import Pmf
#from sqlalchemy import create_engine
# Import smtplib for the actual sending function.
import smtplib

# Here are the email package modules we'll need.
from email.message import EmailMessage

# Create the container email message.
msg = EmailMessage()
msg['Subject'] = 'Your Product Data from Helix Control-M!'
# me == the sender's email address
# family = the list of all recipients' email addresses
msg['From'] = 'jon_fink@bmc.com'
#msg['To'] = 'anieves@bmc.com'
msg['To'] = sys.argv[1]
msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'
body = 'Thank you for Joining us during the Tech Day session!\n\n Please enjoy the the results of your impressive data pipeline.'

msg.attach(body)

plt.style.use('ggplot')
sns.set_palette('colorblind')
sns.set_context('notebook')

def mysql(query, cursor):
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    df = pd.DataFrame(rows, columns=column_names)
    return df

def sql(query):
    return ps.sqldf(query)
  
'''
Connecting to MySQL
'''
db_prefix = sys.argv[2]
print(db_prefix)
# Creating a connection object
connection = pymysql.connect(host ='dba-techday-1.czimjufijgjh.us-east-1.rds.amazonaws.com',port=int(3306),user='dbaadmin',passwd='bmcAdm1n',db=db_prefix+'_whiskey_retail_shop')
#engine = create_engine(f"mysql+pymysql://dbaadmin:bmcAdm1n@dba-techday-1.czimjufijgjh.us-east-1.rds.amazonaws.com:3306/{db_prefix}_whiskey_retail_shop")
#connection = engine.connect()
# Creating a cursor object
cursor = connection.cursor()

'''
Pulling Data for Analysis
'''
# Creating the query
query = '''
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
left join whiskey_retail_shop.customers c
on f.customer_id = c.customer_id
left join whiskey_retail_shop.countries as co
on co.country_id = c.country_id 
left join dwh_employees as e
on e.employee_id = f.employee_id
left join dwh_date d
on d.Date_key = f.Date_key
order by f.date '''

# Generating a Dataframe according to the query
df = mysql(query, cursor)
print(df)

'''
Pre-Processing
'''
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
        
        
'''
Q1 — Which products produce the most profit?
'''
# Generating a Dataframe containing the 5 most profitable products
query = '''
select 
    count(*) as Number_Of_Transactions, 
    Product_Name, 
    sum(Alcohol_Price) as Profit
    
from df
group by Product_Name
order by sum(Alcohol_Price) desc
limit 5
'''

top_5_products = sql(query)

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

msg.add_attachment(img_data, maintype='image',
                                 subtype='png')

'''
Q2 — Which products people usually buy?
'''

query = '''
select 
    count(*) as Number_Of_Transactions, 
    Product_Name
    
from df
group by Product_Name
order by count(*) desc
'''

most_bought_products = sql(query)

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
print(probablity_Dataframe)

'''
Q3 — Are there any interesting patterns as to when customers like to buy whiskey? If so what are they?
'''
query = '''
select 
    count(*) as Number_Of_Transactions, 
    Month
    
from df
group by Month
order by count(*)
'''

most_bought_products_by_month = sql(query)

print(most_bought_products_by_month)

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

msg.add_attachment(img_data, maintype='image',
                                 subtype='png')

'''
Q4 — Are we growing as a company in terms of profits or not?
'''

query = '''
select 
    sum(Alcohol_Price) as Profit, 
    year
    
from df
where year != 2022
group by year
order by year asc
'''

profits_by_year = sql(query)

x = profits_by_year.Year
y = np.cumsum(profits_by_year.Profit)

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

msg.add_attachment(img_data, maintype='image',
                                 subtype='png')

'''
Q5 — From which counties do most of the customers come from
'''
query = '''
select 
    count(distinct customer_name) as Number_of_customers, 
    customer_country
    
from df
group by customer_country
order by customer_country asc
'''

customers_by_country = sql(query)
customers_by_country['Number_of_customers'] = pd.to_numeric(customers_by_country['Number_of_customers'], errors='coerce')
# Filtering the top ten percentile of countries
customers_by_country = customers_by_country.sort_values(by = 'Number_of_customers', ascending=False)
topTenPc = int(len(customers_by_country.index)/10)
print(f"topTenPc: {topTenPc}")
top_ten_percentile = customers_by_country.nlargest(topTenPc, 'Number_of_customers')

print(f"top_ten_percentile: {top_ten_percentile}")

sns.barplot(data =top_ten_percentile, x='Number_of_customers', y='customer_country', palette='colorblind')
filename = '/opt/airflow/data/customer_by_country.png'
plt.savefig(filename)
#plt.show()

fp = open(filename, 'rb') 
img_data = fp.read()

msg.add_attachment(img_data, maintype='image',
                                 subtype='png')


# Send the email via our own SMTP server.
with smtplib.SMTP_SSL('email-smtp.us-east-2.amazonaws.com', '465') as s:
    s.login(user='AKIAVVZZ2EN62EVC2CGS', password='BOH+Y4Qb40EWBww/hk8aHFGY+RpgWxJ63gTrj5+Eswur')
    s.send_message(msg)

print("send email")
