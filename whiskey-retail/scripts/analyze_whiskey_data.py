from airflow.operators.bash import BashOperator
from airflow.models.dag import DAG
from datetime import datetime

with DAG(
    dag_id='analyze_whiskey_data',
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "user_code": "tus"
    }
) as dag:
    run_background_script = BashOperator(
        task_id='run_background_script',
        bash_command='cd /root/scripts && nohup /root/scripts/analyze_wrapper.sh ${CTM_USER_CODE} > /dev/null 2>&1 &'
    )
