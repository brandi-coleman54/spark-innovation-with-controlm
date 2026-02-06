#!/bin/bash

local user_code=$1
local api_endpoint=$2
local api_token=$3
local plugins=$4
ctm_env=agent_provisioning

# Run from user home
cd ~ || {
    echo "Error: cannot cd to ~"
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

# --- Install Azure Databricks plugin ---
tries=0
until ctm provision image ZDX_plugin.Linux; do
  ((tries++))
  if [ "\$tries" -ge 3 ]; then
    echo "Failed installation of SAP plugin after \$tries attempt."
    ctm env del admin
    exit 4
  fi
  echo "Installation failed (attempt \$tries). Retrying in 10s..."
  sleep 10
done

# --- Install Databricks plugin ---
tries=0
until ctm provision image DBX_plugin.Linux; do
  ((tries++))
  if [ "\$tries" -ge 3 ]; then
    echo "Failed installation of SAP plugin after \$tries attempt."
    ctm env del admin
    exit 4
  fi
  echo "Installation failed (attempt \$tries). Retrying in 10s..."
  sleep 10
done

ctm deploy /home/controlm/labs/control-m-for-databricks/local_repo/cp_azure_databricks.json

ctm env del ${ctm_env}
echo "Agent install invoked successfully for ${target}."
