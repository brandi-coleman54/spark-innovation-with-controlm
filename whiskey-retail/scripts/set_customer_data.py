import numpy as np
import pandas as pd
import names
from faker import Faker
faker = Faker()

# Generating 1000 Customer Unique id's
customer_id = np.random.default_rng().choice(999999, 1000, replace = False)

# Verify that there are as many ids as there are customers
assert len(set(customer_id)) == 1000

# Verify that the new ids are unique
assert len(pd.Series(customer_id).unique()) == len(customer_id)

# Generating 1000 Customers Data
customer_first_name = []
customer_last_name = []
customer_full_name = []
customer_email = []
customer_last_four_digits = []
customer_country = []
customer_country_code = []
customer_street = []
customer_credit_card_company = []


# iterate through the customers and generate random data
for i in range(len(customer_id)): 
    customer_first_name.append(names.get_first_name())
    customer_last_name.append(names.get_last_name())
    customer_full_name.append(customer_first_name[i] + ' ' + customer_last_name[i])
    customer_email.append(customer_first_name[i] + customer_last_name[i][0].lower() + '@gmail.com')
    customer_last_four_digits.append(np.random.randint(low = 1000, high = 9999, size = 1)[0])
    customer_country.append(faker.country())
    customer_country_code.append(customer_country[i][0:3].upper())
    customer_street.append(faker.street_address())
    customer_credit_card_company.append(faker.credit_card_provider())
    
# Create a customer dataframe
customer_df = pd.DataFrame(customer_id, columns = ['customer_id'])
customer_df['first_name'] = customer_first_name
customer_df['last_name'] = customer_last_name
customer_df['full_name'] = customer_full_name
customer_df['email'] = customer_email
customer_df['country'] = customer_country
customer_df['country_code'] = customer_country_code
customer_df['street'] = customer_street
customer_df['credit_provider'] = customer_credit_card_company
customer_df['four_digits'] = customer_last_four_digits

customer_df.to_csv("/mft_mountPath/customers.csv")
