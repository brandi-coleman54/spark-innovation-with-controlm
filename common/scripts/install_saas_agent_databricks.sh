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
        ctm env del ${ctm_env}
        exit 4
    fi
    echo "Install failed (attempt ${tries}). Retrying in 10s..."
    sleep 10
done

# --- Install Azure Databricks plugin ---
tries=0
until ctm provision image ZDX_plugin.Linux; do
  ((tries++))
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of SAP plugin after $tries attempt."
    ctm env del ${ctm_env}
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  sleep 10
done

# --- Install Databricks plugin ---
tries=0
until ctm provision image DBX_plugin.Linux; do
  ((tries++))
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of SAP plugin after $tries attempt."
    ctm env del ${ctm_env}
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  sleep 10
done

ctm deploy /home/controlm/labs/control-m-for-databricks/local_repo/cp_azure_databricks.json

ctm env del ${ctm_env}
echo "Agent install invoked successfully for ${target}."
