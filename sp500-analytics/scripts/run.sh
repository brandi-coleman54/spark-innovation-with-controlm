# (optional) create a venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# install deps
pip install streamlit pandas altair pyarrow numpy

# put your CSV here (or upload in the UI)
mkdir -p data
# data/sp500_5yr.csv

# save the code below as app.py
streamlit run app.py
