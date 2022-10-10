import pathlib
import pickle

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

import weekly_gas_price_data_module


def dag_setup():
    pickle_folder = pathlib.Path("/tmp").joinpath("weekly_gas_price_data")
    if not pickle_folder.exists():
        pickle_folder.mkdir()


def dag_teardown():
    pickle_files = (
        pathlib.Path("/tmp").joinpath("weekly_gas_price_data").glob("*.pickle")
    )
    for f in pickle_files:
        f.unlink()


def task_weekly_gas_price_data():

    df_long = weekly_gas_price_data_module.get_weekly_gas_price_data()

    pickle.dump(
        df_long, open("/tmp/weekly_gas_price_data/variable_df_long.pickle", "wb")
    )
    
    df_long.to_csv('weekly_gas_price_data_long.csv', index=False)


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="weekly_gas_price_data_dag",
    schedule_interval="@weekly",
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
) as dag:

    setup = PythonOperator(
        task_id="dag_setup",
        python_callable=dag_setup,
    )

    teardown = PythonOperator(
        task_id="dag_teardown",
        python_callable=dag_teardown,
    )

    weekly_gas_price_data = PythonOperator(
        task_id="weekly_gas_price_data_task",
        python_callable=task_weekly_gas_price_data,
    )

    setup >> weekly_gas_price_data

    weekly_gas_price_data >> teardown
