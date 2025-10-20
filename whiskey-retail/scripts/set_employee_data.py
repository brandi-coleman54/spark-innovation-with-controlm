import numpy as np
import pandas as pd
import names
from faker import Faker
faker = Faker()

# Generating 100 Employee Unique id's
employee_id = np.random.default_rng().choice(4000, 100, replace = False)

# Verify that there are as many ids as there are employees
assert len(set(employee_id)) == 100

# Verify that the new ids are unique
assert len(pd.Series(employee_id).unique()) == len(employee_id)

# Generating 100 Employee Data
employee_first_name = []
employee_last_name = []
employee_full_name = []
employee_email = []
employee_city = []
departments = ['Sales', 'Finance', 'Marketing', 'BI']
employee_department = []

# iterate through the employees and generate random data
for i in range(len(employee_id)):
    employee_first_name.append(names.get_first_name())
    employee_last_name.append(names.get_last_name())
    employee_full_name.append(employee_first_name[i] + ' ' + employee_last_name[i])
    employee_email.append(employee_first_name[i] + employee_last_name[i][0].lower() + '@gmail.com')
    employee_city.append(faker.city())
    employee_department.append(np.random.choice(departments, 1)[0])
    
# Create an employee dataframe
employee_df = pd.DataFrame(employee_id, columns = ['employee_id'])
employee_df['first_name'] = employee_first_name
employee_df['last_name'] = employee_last_name
employee_df['full_name'] = employee_full_name
employee_df['email'] = employee_email
employee_df['city'] = employee_city
employee_df['department'] = employee_department

employee_df.to_csv("/mft_mountPath/employees.csv")
