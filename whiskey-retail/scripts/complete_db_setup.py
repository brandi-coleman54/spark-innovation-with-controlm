import sys
import pymysql

connection = pymysql.connect(host ='dba-techday-1.czimjufijgjh.us-east-1.rds.amazonaws.com',port=int(3306),user='dbaadmin',passwd='bmcAdm1n')

db_prefix = sys.argv[1]
print(db_prefix)

cursor = connection.cursor()

cursor.execute('''use '''+ db_prefix +'''_whiskey_retail_shop;''')

# Creating customer query
query = '''
drop table if exists dwh_customers;'''

# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()

query = '''
create table dwh_customers as
select
	c1.customer_id,
    c1.first_name,
    c1.last_name,
    c1.full_name,
    c2.country_code
from '''+ db_prefix +'''_whiskey_retail_shop.customers as c1
join '''+ db_prefix +'''_whiskey_retail_shop.countries as c2
on c1.country_id = c2.country_id
order by customer_id;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()


query = '''
alter table dwh_customers
modify column customer_id int not null primary key;'''

# Execute the query
cursor.execute(query)


# Creating employee query
query = '''
drop table if exists dwh_employees;'''

# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()

query = '''
create table dwh_employees as
select 
	e.employee_id,
    e.first_name,
    e.last_name,
    e.full_name,
    d.department
from '''+ db_prefix +'''_whiskey_retail_shop.employees as e
join '''+ db_prefix +'''_whiskey_retail_shop.departments as d
on e.department_id = d.department_id
order by employee_id;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()

query = '''
alter table dwh_employees
modify column employee_id int not null primary key;'''

# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()


# Creating product query
query = '''
create table dwh_products as
select *
from '''+ db_prefix +'''_whiskey_retail_shop.products 
order by product_id;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()

query = '''
alter table dwh_products
modify column product_id int not null primary key;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()

# Creating fact query
query = '''
drop table if exists dwh_fact;
'''
    
# Execute the query
cursor.execute(query)
connection.commit()

query = '''
CREATE TABLE dwh_fact AS 
SELECT c1.customer_id,
    e1.employee_id,
    p2.product_id,
    p2.Alcohol_Amount,
    p2.Alcohol_Percent,
    p2.Alcohol_Price,
    p2.Product_Name,
    c1.four_digits,
    c2.Country,
    c3.credit_provider,
    d.Date_key,
    p1.date 
FROM
    whiskey_retail_shop.payments AS p1
        JOIN
    whiskey_retail_shop.customers AS c1 ON p1.customer_id = c1.customer_id
        JOIN
    whiskey_retail_shop.employees AS e1 ON p1.employee_id = e1.employee_id
        JOIN
    whiskey_retail_shop.products AS p2 ON p1.product_id = p2.product_id
        JOIN
    whiskey_retail_shop.countries AS c2 ON c1.country_id = c2.country_id
        JOIN
    whiskey_retail_shop.customer_cc AS c3 ON c1.credit_provider_id = c3.credit_provider_id
        JOIN
    dwh_date AS d ON p1.date = d.Dates
ORDER BY d.Dates;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()

#Setting the foreign keys for each dimension table
query = '''
alter table dwh_fact
add foreign key (customer_id)  references dwh_customers ( customer_id);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()

query = '''
alter table dwh_fact
add foreign key (employee_id)  references dwh_employees ( employee_id);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()

query = '''
alter table dwh_fact
add foreign key (product_id)  references dwh_products ( product_id);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()


query = '''
alter table dwh_fact
add foreign key (Date_key)  references dwh_date ( Date_key);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()

# Create trigger insert_customer
query = '''
create trigger insert_customer
after insert on '''+ db_prefix +'''_whiskey_retail_shop.customers 
for each row
insert into '''+ db_prefix +'''_whiskey_retail_shop.dwh_customers
select 
	c1.customer_id,
    c1.first_name,
    c1.last_name,
    c1.full_name,
    c2.country_code
from customers as c1
join countries as c2
on c1.country_id = c2.country_id
where c1.customer_id = new.customer_id;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()


# Create trigger insert_employee
query = '''
create trigger insert_employee
after insert on '''+ db_prefix +'''_whiskey_retail_shop.employees 
for each row
insert into '''+ db_prefix +'''_whiskey_retail_shop.dwh_employees
select 
	e.employee_id,
    e.first_name,
    e.last_name,
    e.full_name,
    d.department
from employees as e
join departments as d
on e.department_id = d.department_id
where e.employee_id = new.employee_id;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()


# Create trigger new_payment
query = '''
create trigger new_payment
after insert on payments
for each row
insert into '''+ db_prefix +'''_whiskey_retail_shop.dwh_fact
select 
	c.customer_id,
    e.employee_id,
    pr.product_id,
    pr.Alcohol_Amount,
    pr.Alcohol_Percent,
    pr.Alcohol_Price,
    pr.Product_Name,
    c.four_digits,
    co.Country,
    cc.credit_provider,
    d.Date_key,
    d.Dates
from payments as p
join customers as c
on p.customer_id = c.customer_id
join countries as co
on c.country_id = co.country_id
join customer_cc cc
on c.credit_provider_id = cc.credit_provider_id
join employees e
on p.employee_id = e.employee_id
join products pr
on p.product_id = pr.product_id
join '''+ db_prefix +'''_whiskey_retail_shop.dwh_date d
on d.Dates = p.date
where p.payment_id = new.payment_id;
'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()