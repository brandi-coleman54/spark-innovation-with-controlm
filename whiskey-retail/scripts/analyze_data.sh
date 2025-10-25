#!/bin/bash

user_code=$1

source ~/venv/bin/activate
cd /mft_mountPath
nohup streamlit run analyze_data.py -- ${user_code} --server.headless true --server.address 0.0.0.0 --server.port 8501 &
