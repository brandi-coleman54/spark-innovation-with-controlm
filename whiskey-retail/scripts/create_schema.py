import sys
import psycopg2
import os

pg_host = os.environ['POSTGRES_POSTGRESQL_SERVICE_HOST']
pg_password = os.environ['PG_PASSWORD']
db_prefix = sys.argv[1]

connection = psycopg2.connect(host=pg_host, port=int(5432), user='postgres',password=pg_password)
cursor = connection.cursor()

query = f"drop schema if exists {db_prefix}_whiskey_retail_shop cascade;"
cursor.execute(query)
query = f"create schema {db_prefix}_whiskey_retail_shop;"
cursor.execute(query)
query = f"SET search_path = {db_prefix}_whiskey_retail_shop;"
cursor.execute(query)
query = '''
    CREATE TABLE countries (
        Country VARCHAR(100) NOT NULL,
        Country_Code VARCHAR(100) NOT NULL,
        country_id INT PRIMARY KEY
    );
'''
cursor.execute(query)
query = '''
    CREATE TABLE customer_cc (
        credit_provider VARCHAR(100) NOT NULL,
        credit_provider_id INT PRIMARY KEY
    );
'''
cursor.execute(query)
query = '''
    CREATE TABLE products (
        Product_Name VARCHAR(100) NOT NULL,
        Alcohol_Percent FLOAT NOT NULL,
        Alcohol_Amount FLOAT NOT NULL,
        Alcohol_Price FLOAT NOT NULL,
        product_id int NOT NULL PRIMARY KEY
    );
'''
cursor.execute(query)
query = '''
    CREATE TABLE departments (
        department_id INT PRIMARY KEY,
        department VARCHAR(100) NOT NULL
    );
'''
cursor.execute(query)
query = '''
    CREATE TABLE customers (
        customer_id INT PRIMARY KEY NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        street VARCHAR(100) NOT NULL,
        four_digits INT NOT NULL,
        country_id INT NOT NULL,
        credit_provider_id INT NOT NULL,
        FOREIGN KEY (country_id) REFERENCES countries (country_id),
        FOREIGN KEY (credit_provider_id) REFERENCES customer_cc (credit_provider_id)
    );
'''
cursor.execute(query)
query = '''
    CREATE TABLE employees (
        employee_id INT PRIMARY KEY NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        city VARCHAR(100) NOT NULL,
        department_id INT NOT NULL,
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    );
'''
cursor.execute(query)
query = '''
    CREATE TABLE payments (
        payment_id INT NOT NULL PRIMARY KEY,
        date DATE NOT NULL,
        customer_id INT NOT NULL,
        employee_id INT NOT NULL,
        product_id INT NOT NULL,
        price FLOAT NOT NULL
    );
'''
cursor.execute(query)
query = '''
    CREATE TABLE dwh_date (
        Date_key INT NOT NULL PRIMARY KEY,
        Dates DATE NOT NULL,
        Day_name VARCHAR(50) NOT NULL,
        Month_name VARCHAR(50) NOT NULL,
        Year_name VARCHAR(50) NOT NULL
    );
'''
cursor.execute(query)


    
# Commit the transaction
connection.commit()