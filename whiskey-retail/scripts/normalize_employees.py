import numpy as np
import pandas as pd
from faker import Faker
faker = Faker()
import pandasql as ps


def sql(query):
    return ps.sqldf(query)

employee_df = pd.read_csv("/mft_mountPath/employees.csv")
employee_id = employee_df['employee_id']

# Extracting the departments from the employees table
departments = pd.Series(employee_df.department.unique()).to_list()

# Generating unique department ids
department_id = [*range(0, len(departments))]

# Creating a table called departments
department_df = pd.DataFrame(department_id, columns=['department_id'])
department_df['department'] = departments

# Extracting the country_id column from customers
query = '''
select department_df.department_id
from employee_df 
join department_df
on 
    employee_df.department = department_df.department
'''

department_ids = sql(query)

# Connecting countries to customers by adding the foregin key: country_id
employee_df['department_id'] = department_ids

# Dropping the column department
employee_df = employee_df.drop('department',axis = 1)

employee_df.to_csv("/mft_mountPath/norm_employees.csv")
department_df.to_csv("/mft_mountPath/departments.csv")
