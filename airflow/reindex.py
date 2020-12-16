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

# eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtb25nbyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJ0ZXN0LXRva2VuLWI2azh0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6InRlc3QiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiI5Y2M3M2ZiMy0zYzcyLTExZWItOTJkMy1mYTE2M2UwZDg4NDEiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6bW9uZ286dGVzdCJ9.BsPaD2Szqc9cpDSdcrKFkH5WC_FU3Cf_iuM2ALs6d-eo55BNZacLy8sXu84gFwpyM08Ug71AjNUJ8BYFEdZ7Fw9N_762Slb5pTqNU_XiH6JBF-DJdqr3xK4OpTC0Va-yrfPYxpGsnbRapAQrOX_uhTtrr3tfRnqFQr_CY8y13ouH-LUlDbiohL5HQKNZyZnvX-w8yqFnNQx9DdVbM2MdCt2QZcXH-BqrxwJ2moXrwbaas1valQ94wIQ8cOyO0CqPys2IPB4i7rubzaB9k-0S9axd1IKJvhrkIPVjTiX-NbiX6tX9FHGXTrFYrJ8lMOkL65pkYxmxwcS78Kn28TvkAA

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
