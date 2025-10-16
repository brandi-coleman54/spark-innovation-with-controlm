from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
import pendulum
import openai

def call_gpt_4o_mini():
        # Retrieve API key from Airflow Connection
        openai_conn = BaseHook.get_connection('openai_api_key')
        openai.api_key = openai_conn.extra_dejson.get('api_key')

        client = openai.OpenAI(api_key=openai.api_key)

        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Explain the concept of DAGs in Airflow."}
                ]
        )
        print(response.choices[0].message.content)

with DAG(
        dag_id='gpt_4o_mini_example',
        start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
        schedule=None,
        catchup=False,
        tags=['openai', 'llm'],
) as dag:
        gpt_task = PythonOperator(
                task_id='call_gpt_4o_mini_task',
                python_callable=call_gpt_4o_mini,
        )
