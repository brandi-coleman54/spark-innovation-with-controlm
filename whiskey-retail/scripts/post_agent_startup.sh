#!/bin/bash

user_code=$1
pg_cluster_ip=$2
pg_password=$3

ready_status="False"
total=0
while true; do
    ready_status=$(kubectl get pod -n ${user_code} ${user_code}-sts-0 -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    if [[ "${ready_status}" == "True" ]]; then
        break
    fi
    sleep 15
    ((total+=15))
    if [ "${total}" -ge 480 ]; then
        break
    fi
done
kubectl -n ${user_code} exec ${user_code}-sts-0 -- /bin/sh -c "python3 -m venv venv"
kubectl -n ${user_code} exec ${user_code}-sts-0 -- /bin/sh -c ". venv/bin/activate && pip install pymysql psycopg2-binary matplotlib empiricaldist seaborn scipy pandasql names faker streamlit"
kubectl -n ${user_code} exec ${user_code}-sts-0 -- /bin/sh -c "export PG_CLUSTER_IP=${pg_cluster_ip} && export PG_PASSWORD=${pg_password}"
kubectl -n ${user_code} exec ${user_code}-sts-0 -- /bin/sh -c "echo \"export PG_CLUSTER_IP=${pg_cluster_ip}\" >> /home/controlm/venv/bin/activate && echo \"export PG_PASSWORD=${pg_password}\" >> /home/controlm/venv/bin/activate"

ready_status="False"
total=0
while true; do
    ready_status=$(kubectl get pod -n ${user_code} "${user_code}-sts-1" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    if [[ "${ready_status}" == "True" ]]; then
        break
    fi
    sleep 15
    ((total+=15))
    if [ "${total}" -ge 480 ]; then
        break
    fi
done
kubectl -n ${user_code} exec ${user_code}-sts-1 -- /bin/sh -c "python3 -m venv venv"
kubectl -n ${user_code} exec ${user_code}-sts-1 -- /bin/sh -c ". venv/bin/activate && pip install pymysql psycopg2-binary matplotlib empiricaldist seaborn scipy pandasql names faker streamlit"
kubectl -n ${user_code} exec ${user_code}-sts-1 -- /bin/sh -c "export PG_CLUSTER_IP=${pg_cluster_ip} && export PG_PASSWORD=${pg_password}"
kubectl -n ${user_code} exec ${user_code}-sts-1 -- /bin/sh -c "echo \"export PG_CLUSTER_IP=${pg_cluster_ip}\" >> /home/controlm/venv/bin/activate && echo \"export PG_PASSWORD=${pg_password}\" >> /home/controlm/venv/bin/activate"
