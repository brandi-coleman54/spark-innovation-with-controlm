#!/bin/bash

user_code=$1

source /root/scripts/venv/bin/activate
nohup streamlit run airflow_analyze_data.py -- ${user_code} --server.headless true --server.port 8501 &
