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
    dag_id='product_function',
    schedule=None,
    start_date=datetime(2021, 1, 1),
    dagrun_timeout=timedelta(minutes=60),
    tags=['product_data'],
    is_paused_upon_creation=False,
    catchup=False,
) as dag:
    # [START howto_lambda_operator]
    productLambdaFunc0 = LambdaInvokeFunctionOperator(
        task_id='set_product_data_func',
        function_name='ctmGetProductData',
        aws_conn_id='aws_default',
        payload='',
    )

    productLambdaFunc0
    # [END howto_lambda_operator]
