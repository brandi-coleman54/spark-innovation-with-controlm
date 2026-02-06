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


# --- Install Jenkins plugin ---
tries=0
until ctm provision image Jenkins_plugin.Linux; do
  ((tries++))
  if [ "\$tries" -ge 3 ]; then
    echo "Failed installation of Jenkins plugin after \$tries attempt."
    ctm env del ${ctm_env}
    exit 4
  fi
  echo "Installation failed (attempt \$tries). Retrying in 10s..."
  sleep 10
done

ctm deploy /home/controlm/labs/forecast-flow-jenkins/local_repo/cp_jenkins.json
ctm deploy /home/controlm/labs/forecast-flow-jenkins/workflows/jenkins.json
ctm env del ${ctm_env}
echo "Agent install invoked successfully for ${target}."
