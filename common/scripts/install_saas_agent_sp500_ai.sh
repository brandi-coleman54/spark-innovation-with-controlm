#!/bin/bash

user_code=$1
api_endpoint=$2
api_token=$3
ctm_env=agent_provisioning

# Run from /home/controlm
cd /home/controlm || {
    echo "Error: cannot cd to /home/controlm"
    exit 3
}

tries=0
target="${user_code}_instruqt_server"

ctm env add ${ctm_env} ${api_endpoint} ${api_token}

until ctm provision saas::install Agent_Ubuntu.Linux sparkit ${target} -e ${ctm_env}; do
    ((tries++))
    if [ "${tries}" -ge "3" ]; then
        echo "Install failed after ${tries} attempts."
        ctm env del admin
        exit 4
    fi
    echo "Install failed (attempt ${tries}). Retrying in 10s..."
    sleep 10
done

# --- Install BigQuery plugin ---
tries=0
until ctm provision image GBQ_plugin.Linux; do
  ((tries++))
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of BigQuery plugin after $tries attempt."
    ctm env del admin
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  sleep 10
done

# --- Install MFT plugin ---
tries=0
until ctm provision image MFT_plugin.Linux; do
  ((tries++))
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of MFT plugin after $tries attempt."
    ctm env del admin
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  sleep 10
done

# --- Install QuickSight plugin ---
tries=0
until ctm provision image AQS_plugin.Linux; do
  ((tries++))
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of QuickSight plugin after $tries attempt."
    ctm env del admin
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  sleep 10
done

# --- Install GCP Vertex AI plugin ---
tries=0
until ctm provision image GCP_Vertex_AI_plugin.Linux; do
  ((tries++))
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of GCP Vertex AI plugin after $tries attempt."
    ctm env del admin
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  sleep 10
done

# --- Install GCP Functions plugin ---
tries=0
until ctm provision image GCP_Functions_plugin.Linux; do
  ((tries++))
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of GCP Functions plugin after $tries attempt."
    ctm env del admin
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  sleep 10
done


ctm deploy /home/controlm/labs/sp500-analytics-ai/local_repo/cp_bigquery.json
ctm deploy /home/controlm/labs/sp500-analytics-ai/local_repo/cp_gcs.json
ctm deploy /home/controlm/labs/sp500-analytics-ai/local_repo/cp_quicksight.json
ctm deploy /home/controlm/labs/sp500-analytics-ai/local_repo/cp_s3.json
ctm deploy /home/controlm/labs/sp500-analytics-ai/local_repo/cp_vertex.json
ctm deploy /home/controlm/labs/sp500-analytics-ai/local_repo/cp_functions.json

rm -rf /home/controlm/labs/sp500-analytics-ai/local_repo/cp*

ctm env del ${ctm_env}
echo "Agent install invoked successfully for ${target}."
