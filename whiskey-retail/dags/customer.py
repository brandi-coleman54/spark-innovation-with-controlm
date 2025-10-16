# To initiate the DAG Object
from airflow import DAG
# Importing datetime and timedelta modules for scheduling the DAGs
from datetime import timedelta, datetime
# Importing operators 
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
import os
from airflow.models.connection import Connection

# Initiating the default_args
default_args = {
        'owner' : 'airflow',
        'start_date' : datetime(2024, 8, 5)
}

with DAG(
    dag_id='customer_functions',
    schedule=None,
    start_date=datetime(2021, 1, 1),
    dagrun_timeout=timedelta(minutes=60),
    tags=['customer_data'],
    is_paused_upon_creation=False,
    catchup=False,
) as dag:
    # [START howto_lambda_operator]
    customerLambdaFunc0 = LambdaInvokeFunctionOperator(
        task_id='set_customer_data_func',
        aws_conn_id='aws_default',
        function_name='ctmSetCustomerData',
        payload='',
    ),
    customerLambdaFunc1 = LambdaInvokeFunctionOperator(
        task_id='norm_customer_data_func',
        aws_conn_id='aws_default',
        function_name='ctmNormCustomerData',
        payload='',
    )

    customerLambdaFunc0 >> customerLambdaFunc1
    # [END howto_lambda_operator]
