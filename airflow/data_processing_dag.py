from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.datasets import Dataset
from datetime import datetime
import pandas as pd
import os
import re

INPUT_FILE = "/opt/airflow/data/input/comments.csv"
OUTPUT_FILE = "/opt/airflow/data/output/processed_comments.csv"

# Dataset для DAG2
processed_csv_dataset = Dataset(OUTPUT_FILE)

def check_file_empty():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"{INPUT_FILE} not found")
    if os.stat(INPUT_FILE).st_size == 0:
        return "log_empty"
    return "processing.process_data"

def process_data():
    print(f"Starting processing: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)

    print("Step 1: Replacing nulls in text columns with '-'")
    text_columns = ['userName', 'userImage', 'content', 'reviewCreatedVersion', 'replyContent']
    df[text_columns] = df[text_columns].fillna("-")

    print("Step 2: Sorting by 'at' column")
    if 'at' in df.columns:
        df['at'] = pd.to_datetime(df['at'], dayfirst=True, errors='coerce', utc=True)
        print("First 5 'at' values after parsing:")
        print(df['at'].head())
        # df = df.dropna(subset=['at'])  # убираем, если не хотим терять строки
        df.sort_values('at', inplace=True)

    print("Step 3: Cleaning content column")
    if 'content' in df.columns:
        df['content'] = df['content'].apply(lambda x: re.sub(r'[^\w\s.,!?]', '', str(x)))
    else:
        print("WARNING: 'content' column not found, skipping cleaning")

    print(f"Writing processed data to: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False, date_format='%Y-%m-%dT%H:%M:%SZ')
    print("Processing complete!")

with DAG(
    dag_id="dag_1_processing",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    wait_for_file = FileSensor(
        task_id="wait_for_file",
        filepath=INPUT_FILE,
        poke_interval=5,
        timeout=120,
        mode="poke",
    )

    branch = BranchPythonOperator(
        task_id="check_file",
        python_callable=check_file_empty,
    )

    log_empty = BashOperator(
        task_id="log_empty",
        bash_command="echo 'File is empty'",
    )

    with TaskGroup("processing") as processing:
        process_task = PythonOperator(
            task_id="process_data",
            python_callable=process_data,
        )

    # DummyOperator для обновления Dataset
    from airflow.operators.empty import EmptyOperator
    update_dataset = EmptyOperator(
        task_id="update_dataset",
        outlets=[processed_csv_dataset],  # <-- помечаем Dataset как обновлённый
    )

    # зависимости
    wait_for_file >> branch
    branch >> log_empty
    branch >> processing >> update_dataset
