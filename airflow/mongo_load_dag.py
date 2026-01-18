from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.datasets import Dataset
from airflow.hooks.base import BaseHook
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
import os

CSV_PATH = "/opt/airflow/data/output/processed_comments.csv"
processed_csv_dataset = Dataset(CSV_PATH)


def load_to_mongo(**kwargs):
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH, low_memory=False)

    df['at'] = pd.to_datetime(df['at'], errors='coerce')

    records = df.to_dict(orient='records')
    for rec in records:
        if pd.isna(rec.get('at')):
            rec['at'] = None

    # 🔥 БЕРЁМ CONNECTION ИЗ AIRFLOW
    conn = BaseHook.get_connection("mongo_default")
    client = MongoClient(conn.get_uri())

    db = client["google_play_reviews"]
    collection = db["comments"]

    if records:
        collection.insert_many(records)

    client.close()


with DAG(
    dag_id="mongo_load_dag",
    start_date=datetime(2026, 1, 1),
    schedule=[processed_csv_dataset],
    catchup=False,
    tags=["mongo", "google_play"],
) as dag:

    load_csv_to_mongo = PythonOperator(
        task_id="load_csv_to_mongo",
        python_callable=load_to_mongo,
    )