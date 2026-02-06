#!/bin/bash

user_code=$1
api_endpoint=$2
api_token=$3
ctm_env=agent_provisioning

echo "$*"

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

tries=0
until ctm config server:agent:mft:ssh:key::generate IN01 ${target} ${user_code}_id ${user_code}${user_code} 2048 -e ${ctm_env}; do
    tries=$((tries +1))
  if [ "$tries" -ge 10 ]; then
    echo "Failed config ssh after $tries attempt."
    ctm env del ${ctm_env}
    exit 4
  fi
  echo "SSH key setup failed (attempt $tries). Retrying in 20s..."
  sleep 20
done

cat ~/ctm/cm/AFT/data/Keys/${user_code}_id.pub >> ~/.ssh/authorized_keys
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
ctm deploy ~/sftp_cp.json

ctm env del ${ctm_env}
echo "Agent install invoked successfully for ${target}."
