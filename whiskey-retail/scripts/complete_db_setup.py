import sys
import psycopg2
import os

pg_host = os.environ['POSTGRES_POSTGRESQL_SERVICE_HOST']
pg_password = os.environ['PG_PASSWORD']
db_prefix = sys.argv[1]

connection = psycopg2.connect(host=pg_host, port=int(5432), user='postgres',password=pg_password)
cursor = connection.cursor()
cursor.execute(f"SET search_path = {db_prefix}_whiskey_retail_shop;")

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
alter column customer_id type int,
alter column customer_id set not null,
add primary key (customer_id);'''

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
alter column employee_id type int,
alter column employee_id set not null,
add primary key (employee_id);'''

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
alter column product_id type int,
alter column product_id set not null,
add primary key (product_id);
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

query = f'''
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
    {db_prefix}_whiskey_retail_shop.payments AS p1
        JOIN
    {db_prefix}_whiskey_retail_shop.customers AS c1 ON p1.customer_id = c1.customer_id
        JOIN
    {db_prefix}_whiskey_retail_shop.employees AS e1 ON p1.employee_id = e1.employee_id
        JOIN
    {db_prefix}_whiskey_retail_shop.products AS p2 ON p1.product_id = p2.product_id
        JOIN
    {db_prefix}_whiskey_retail_shop.countries AS c2 ON c1.country_id = c2.country_id
        JOIN
    {db_prefix}_whiskey_retail_shop.customer_cc AS c3 ON c1.credit_provider_id = c3.credit_provider_id
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
add foreign key (customer_id) references dwh_customers ( customer_id);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()

query = '''
alter table dwh_fact
add foreign key (employee_id) references dwh_employees (employee_id);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()

query = '''
alter table dwh_fact
add foreign key (product_id) references dwh_products (product_id);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()


query = '''
alter table dwh_fact
add foreign key (Date_key) references dwh_date (Date_key);
'''
    
# Execute the query
cursor.execute(query)
connection.commit()

# Create trigger insert_customer
old_query = '''
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

query = f'''
CREATE OR REPLACE FUNCTION log_customer_to_dwh()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO {db_prefix}_whiskey_retail_shop.dwh_customers (
        customer_id,
        first_name,
        last_name,
        full_name,
        country_code
    )
    SELECT
        NEW.customer_id,
        NEW.first_name,
        NEW.last_name,
        NEW.full_name,
        c2.country_code
    FROM {db_prefix}_whiskey_retail_shop.countries AS c2
    WHERE NEW.country_id = c2.country_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;'''
    
# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()


# Create trigger insert_employee
old_query = '''
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
query = f'''
CREATE OR REPLACE FUNCTION log_employee_to_dwh()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO {db_prefix}_whiskey_retail_shop.dwh_employees (
        employee_id,
        first_name,
        last_name,
        full_name,
        department
    )
    SELECT
        NEW.employee_id,
        NEW.first_name,
        NEW.last_name,
        NEW.full_name,
        d.department
    FROM {db_prefix}_whiskey_retail_shop.departments AS d
    WHERE NEW.department_id = d.department_id;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;'''


# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()


# Create trigger new_payment
old_query = '''
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

query = f'''
CREATE OR REPLACE FUNCTION new_payment_to_dwh()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO {db_prefix}_whiskey_retail_shop.dwh_fact (
        customer_id,
        employee_id,
        product_id,
        "Alcohol_Amount",
        "Alcohol_Percent",
        "Alcohol_Price",
        "Product_Name",
        four_digits,
        "Country",
        credit_provider,
        "Date_key",
        "Dates"
    )
    SELECT
        c.customer_id,
        e.employee_id,
        pr.product_id,
        pr."Alcohol_Amount",
        pr."Alcohol_Percent",
        pr."Alcohol_Price",
        pr."Product_Name",
        c.four_digits,
        co."Country",
        cc.credit_provider,
        d."Date_key",
        d."Dates"
    FROM payments AS p
    JOIN customers AS c ON p.customer_id = c.customer_id
    JOIN countries AS co ON c.country_id = co.country_id
    JOIN customer_cc AS cc ON c.credit_provider_id = cc.credit_provider_id
    JOIN employees AS e ON p.employee_id = e.employee_id
    JOIN products AS pr ON p.product_id = pr.product_id
    JOIN {db_prefix}_whiskey_retail_shop.dwh_date AS d ON d."Dates" = p.date
    WHERE p.payment_id = NEW.payment_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;'''


# Execute the query
cursor.execute(query)
    
# Commit the transaction
connection.commit()
