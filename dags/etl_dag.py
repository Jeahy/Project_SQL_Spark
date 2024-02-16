from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from e-commerce_data_pipeline.scripts.imp_clean_trans_script import clean_transform_main
from e-commerce_data_pipeline.scripts.config import input_raw, output_transformed

default_args = {
    'owner': 'jessica',
    'depends_on_past': False,
    'start_date': datetime(2022, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    dag_id = 'spark_project_dag',
    description='Dag for a sql spark project',
    tags=['jessica', 'spark'],
    default_args=default_args,
    schedule_interval='@daily',  # Set your desired schedule
    catchup=False,
)


import_clean_transform_task = PythonOperator(
    task_id = 'import_clean_transform',
    python_callable = clean_transform_main,
    op_args=[input_raw, output_transformed],
    provide_context=True,  # Pass the Airflow context to the function
    dag = dag,
)


import_clean_transform_task