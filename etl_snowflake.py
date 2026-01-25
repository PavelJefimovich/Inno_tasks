from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

with DAG(
    dag_id='etl_airline_snowflake',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    template_searchpath=['/opt/airflow/sql/procedures'],
    doc_md="""
        # ETL Pipeline for Airline DWH
        This DAG loads data from STG streams into DIM and FACT tables
        and logs row counts in AUDIT_LOG.
    """
) as dag:

    # ---- Staging ----
    stg_passengers = SnowflakeOperator(
        task_id='stg_passengers',
        snowflake_conn_id='my_snowflake_conn',
        sql='CALL PROC_LOAD_PASSENGERS();',
        autocommit=True,
        doc_md="Load PASSENGERS from STG stream and log row count"
    )

    stg_airports = SnowflakeOperator(
        task_id='stg_airports',
        snowflake_conn_id='my_snowflake_conn',
        sql='CALL PROC_LOAD_AIRPORTS();',
        autocommit=True,
        doc_md="Load AIRPORTS from STG stream and log row count"
    )

    stg_flights = SnowflakeOperator(
        task_id='stg_flights',
        snowflake_conn_id='my_snowflake_conn',
        sql='CALL PROC_LOAD_FLIGHTS();',
        autocommit=True,
        doc_md="Load FLIGHTS from STG stream and log row count"
    )

    # ---- Dimensions ----
    dim_passenger = SnowflakeOperator(
        task_id='dim_passenger',
        snowflake_conn_id='my_snowflake_conn',
        sql='CALL PROC_DIM_PASSENGER();',
        autocommit=True,
        doc_md="Populate DIM.PASSENGER and log row count"
    )

    dim_airport = SnowflakeOperator(
        task_id='dim_airport',
        snowflake_conn_id='my_snowflake_conn',
        sql='CALL PROC_DIM_AIRPORT();',
        autocommit=True,
        doc_md="Populate DIM.AIRPORT and log row count"
    )

    dim_date = SnowflakeOperator(
        task_id='dim_date',
        snowflake_conn_id='my_snowflake_conn',
        sql='CALL PROC_DIM_DATE();',
        autocommit=True,
        doc_md="Populate DIM.DATE and log row count"
    )

    # ---- Fact ----
    fact_flights = SnowflakeOperator(
        task_id='fact_flights',
        snowflake_conn_id='my_snowflake_conn',
        sql='CALL PROC_FACT_FLIGHTS();',
        autocommit=True,
        doc_md="Populate FACT.FLIGHTS and log row count"
    )

    # ---- Dependencies ----
    stg_passengers >> dim_passenger >> fact_flights
    stg_airports >> dim_airport >> fact_flights
    stg_flights >> dim_date >> fact_flights
