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
        ctm env del ${ctm_env}
        exit 4
    fi
    echo "Install failed (attempt ${tries}). Retrying in 10s..."
    sleep 10
done

# --- Install MFT plugin ---
tries=0
until ctm provision image MFT_plugin; do
  ((tries++))
  if [ "\$tries" -ge 3 ]; then
    echo "Failed installation of MFT plugin after \$tries attempt."
    ctm env del ${ctm_env}
    exit 4
  fi
  echo "Installation failed (attempt \$tries). Retrying in 10s..."
  sleep 10
done

ctm config server:agent:mft:ssh:key::generate IN01 ${user_code}_instruqt_server ${user_code}_id ${user_code}${user_code} 2048
cat ~/ctm/cm/AFT/data/Keys/${user_cod}_id.pub >> ~/.ssh/authorized_keys
cat > ~/sftp_cp.json <<EOF
{
  "${user_code^^}_SFTP": {
    "Type": "ConnectionProfile:FileTransfer:SFTP",
    "VerifyBytes": true,
    "SSHCompression": false,
    "User": "controlm",
    "Passphrase": "${user_code}${user_code}",
    "PrivateKeyName": "${user_code}_id",
    "HostName": "localhost",
    "Description": "",
    "Centralized": true
  }
}
EOF

ctm env del ${ctm_env}
echo "Agent install invoked successfully for ${target}."
