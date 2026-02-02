#!/bin/bash

# (optional) create a venv
cd /home/controlm/labs
python -m venv .venv
source .venv/bin/activate

# install deps
pip install streamlit pandas altair pyarrow numpy
