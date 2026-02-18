#!/bin/bash

source ~/venv/bin/activate

# save the code below as app_predictions.py
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
streamlit run app_predictions.py --server.headless true --server.address 0.0.0.0 --server.port 30003
