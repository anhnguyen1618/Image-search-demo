from airflow import DAG
from airflow import configuration as conf
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

default_args = {
    'owner': 'Zozo',
    'depends_on_past': False,
    'start_date': days_ago(0),
    'email': 'airflow@example.com',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'kubernetes_sample', default_args=default_args, catchup=False, schedule_interval=timedelta(minutes=5))


reindex = KubernetesPodOperator(namespace='default',
                                image="eu.gcr.io/gothic-module-289816/openshift-cli:v2",
                                cmds=["sh", "reindex.sh"],
                                env_vars={'TOKEN': '{{ var.value.Token}}'},
                                labels={"test-airflow": "firstversion"},
                                name="reindex",
                                task_id="reindex-task",
                                get_logs=True,
                                dag=dag
                                )

test = KubernetesPodOperator(namespace='default',
                                image="eu.gcr.io/gothic-module-289816/openshift-cli:v2",
                                cmds=["echo"],
                                arguments=["heloo world{{ds}}"],
                                env_vars={'TOKEN': '{{ var.value.Token}}'},
                                labels={"test-airflow": "firstversion"},
                                name="test",
                                task_id="test-task",
                                get_logs=True,
                                dag=dag
                                )
test.set_upstream(reindex)