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

tries=1
target="${user_code}_instruqt_server"

ctm env add ${ctm_env} ${api_endpoint} ${api_token}

until ctm provision saas::install Agent_Ubuntu.Linux sparkit ${target} -e ${ctm_env}; do
    if [ "${tries}" -ge "3" ]; then
        echo "Install failed after ${tries} attempts."
        ctm env del ${ctm_env}
        exit 4
    fi
    echo "Install failed (attempt ${tries}). Retrying in 10s..."
    ((tries++))
    sleep 10
done


# --- Install Snowflake plugin ---
tries=1
until ctm provision image SNF_plugin.Linux; do
  if [ "$tries" -ge 3 ]; then
    echo "Failed installation of Snowflake plugin after $tries attempt."
    ctm env del ${ctm_env}
    exit 4
  fi
  echo "Installation failed (attempt $tries). Retrying in 10s..."
  ((tries++))
  sleep 10
done


ctm env del ${ctm_env}
echo "Agent install invoked successfully for ${target}."
