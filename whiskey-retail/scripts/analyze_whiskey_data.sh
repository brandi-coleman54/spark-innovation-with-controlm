#!/bin/bash

user_code=$1

source /root/scripts/venv/bin/activate
streamlit run analyze_data.py -- ${user_code} --server.headless true --server.port 8501
