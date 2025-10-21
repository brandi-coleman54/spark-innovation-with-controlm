#!/bin/bash

function Check_Mode_Vars {
    if [[ -z "${CTM_AAPI_ENDPOINT}" ]]; then
        echo "Warning: env variable CTM_AAPI_ENDPOINT not set!"
    fi
    if [[ -z "${CTM_PRV_ENV}" ]]; then
        echo "Warning: env variable CTM_PRV_ENV not set!"
    fi
    if [[ -z "${CTM_USER_ENV}" ]]; then
        echo "Warning: env variable CTM_USER_ENV not set!"
    fi
    if [[ -z "${CTM_PRV_TOKEN}" ]]; then
        echo "Warning: env variable CTM_PRV_TOKEN not set!"
    fi
    if [[ -z "${INSTRUQT_USER_EMAIL:-}" ]]; then
        export MODE=TEST
        if [[ -z "${CTM_TST_TOKEN}" ]]; then
            echo "Warning: env variable CTM_TST_TOKEN not set!"
        else
            CTM_AUTH_TOKEN=${CTM_TST_TOKEN}
        fi
        if [[ -z "${CTM_TST_ROLE}" ]]; then
            echo "Warning: env variable CTM_TST_ROLE not set!"
        fi
    else
        export MODE=INVITE
    fi
    agent variable set MODE ${MODE}
}

function Set_User_Data {

    gen_random_code=$1

    if [ "${MODE}" == "INVITE" ]; then

        export CTM_USER_NAME="${INSTRUQT_USER_NAME}"
        export CTM_USER=${INSTRUQT_USER_EMAIL}
        # Split the full name into first_name and last_name variables.
        read -r first_name last_name <<< "$INSTRUQT_USER_NAME"
        # Check if both a first name and a last name were successfully extracted.
        if [ -z "$last_name" ]; then
            echo "Usage: $0 \"Firstname Lastname\""
            echo "Error: Please provide both a first and a last name separated by a space."
        fi
        # --- User Code Generation ---
        # Get the first character of the first name.
        # This is an example of substring extraction in bash.
        first_initial=${first_name:0:1}
        # Get the first two characters of the last name.
        last_initials=${last_name:0:2}
        # Generate a random single-digit number (from 0 to 9).
        random_digit=$((RANDOM % 10))
        # Concatenate the parts to create the final user code.
        if [[ "$gen_random_code" = "random_code" ]]; then
          export CTM_USER_CODE=$(Generate_User_Code)
        else
          export CTM_USER_CODE=$(echo "${first_initial}${last_initials}${random_digit}" | tr '[:upper:]' '[:lower:]')
        fi
    else
        export CTM_USER="tst-inst@example.com"
        export CTM_USER_NAME="Test User"
        export CTM_USER_CODE="tus"
    fi
    # Setting instruqt agent variable for future retrieval
    export CTM_UC_USER_CODE=${CTM_USER_CODE^^}
    agent variable set CTM_USER "${CTM_USER}"
    agent variable set CTM_USER_NAME "${CTM_USER_NAME}"
    agent variable set CTM_USER_CODE "${CTM_USER_CODE}"
    agent variable set CTM_UC_USER_CODE "${CTM_UC_USER_CODE}"
}

function Generate_User_Code {

  alpha=$(head /dev/urandom | tr -dc a-z | head -c 3)
  numeric=$(head /dev/urandom | tr -dc 0-9 | head -c 1)
  echo "${alpha}${numeric}"

}

function Setup_GH_PK {
  private_key=$1
  pk_filename=$2
  known_hosts=$3
  repo_alias=$4

  if [[ -z "${private_key}" ]]; then
        echo "Error: Secret private_key not set!"
        exit 8
  fi
  if [[ -z "${known_hosts}" ]]; then
        echo "Error: Secret known_hosts not set!"
        exit 8
  fi
  echo "${known_hosts}" >> ~/.ssh/known_hosts
  echo "${private_key}" > ~/.ssh/${pk_filename}
  chmod 400 ~/.ssh/${pk_filename}
  cat >> ~/.ssh/config <<EOF
Host ${repo_alias}
 HostName github.com
 User git
 IdentityFile ~/.ssh/${pk_filename}
EOF
}

function Create_TD_Role {
    user_code=$1
    set +e
    user_code=${user_code} uc_user_code=${user_code^^} envsubst < /tmp/role_template_file.json > /tmp/role_def_sub.json

    ctm config authorization:roles::get -s "role=${user_code}" | grep ${user_code}
    
    if [ $? -eq 0 ]; then
        echo "Role ${user_code} already exists."
    else
        echo "Creating Role ${user_code}"
        ctm config authorization:role::add /tmp/role_def_sub.json
    fi
    set -e
}

function Create_TD_User {
    user=$1
    user_code=$2
    set +e
    ctm config authorization:user::get ${user} > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "User ${user} already exists, adding role to existing user instead."
        
    else
        user=${user} user_code=${user_code} envsubst < /tmp/user_template_file.json > /tmp/user_def_sub.json
        echo "Adding user ${user} using /tmp/user_def_sub.json"
        ctm config authorization:user::add /tmp/user_def_sub.json 
    fi
    set -e
}

function Create_TD_Token {
  
    export CTM_AUTH_TOKEN=$(ctm authentication token::create -f /tmp/token_template_file.json | jq -r '.tokenValue') 
    agent variable set CTM_AUTH_TOKEN "${CTM_AUTH_TOKEN}"
    if [[ -n "$CTM_AUTH_TOKEN" && "$CTM_AUTH_TOKEN" != "null" ]]; then
        export CTM_AUTH_TOKEN
        echo "CTM_AUTH_TOKEN successfully created and exported."
    else
        echo "Failed to create CTM authentication token."
    fi
}

function Build_User_Template {
    user_code=$1
    user=$2

    touch /tmp/user_template_file.json
    cat << EOF > /tmp/user_template_file.json
{
    "Name": "${user}",
    "Roles": [
       "${user_code}"
    ]
}
EOF
}

function Build_Token_Template {
  user_code=$1
  
  touch /tmp/token_template_file.json
  cat << EOF > /tmp/token_template_file.json
{
    "tokenName": "${user_code}",
    "Roles": [
       "${user_code}"
    ]
}
EOF
}

function Build_Role_Template {
  user_code=$1
  uc_user_code=$2

  touch /tmp/role_template_file.json
  cat << EOF > /tmp/role_template_file.json
{
  "Name": "${user_code}",
  "AllowedJobs": {
    "Included": [
      [
        [
          "Folder",
          "like",
          "${user_code}*"
        ]
      ]
    ]
  },
  "AllowedJobActions": {
    "ViewProperties": true,
    "Documentation": true,
    "Log": true,
    "Statistics": true,
    "ViewOutputList": true,
    "ViewJcl": true,
    "Why": true,
    "Hold": true,
    "Free": true,
    "Confirm": true,
    "Rerun": true,
    "React": true,
    "Restart": true,
    "Kill": true,
    "Bypass": true,
    "Delete": true,
    "Undelete": true,
    "SetToOk": true,
    "EditProperties": true,
    "EditJcl": true
  },
  "Privileges": {
    "ClientAccess": {
      "ControlmWebClientAccess": "Full",
	  "ApplicationIntegratorAccess": "Browse",
      "AutomationAPIAccess": "Full"
    },
	"ConfigurationManager": {
      "Configuration": "Browse",
      "ControlmSecurity": "Full"
    },
    "Tools": {
      "SiteStandardPolicies": "Browse"
    },
	"ViewpointManager": {
      "Viewpoints": "Browse"
    }
  },
  "Folders": [
    {
      "Privilege": "Full",
      "ControlmServer": "*",
      "Folder": "${user_code}*",
      "Run": true
    }
  ],
  "RunasUsers": [
    {
      "ControlmServer": "*",
      "RunasUser": "*",
      "Host": "${user_code}*"
    }
  ],
  "SiteStandard": [
    {
      "Privilege": "Browse",
      "Name": "*"
    }
  ],
  "Secrets": [
    {
      "Privilege": "Browse",
      "Name": "${user_code}*"
    }
  ],
  "SiteCustomization": [
    {
      "Privilege": "Browse",
      "Name": "*"
    }
  ],
  "AgentManagement": [
    {
      "ControlmServer": "*",
      "Agent": "sparkit",
      "Privilege": "Full"
    }
  ],
  "PluginManagement": [
    {
      "ControlmServer": "*",
      "Agent": "sparkit",
      "PluginType": "*",
      "Privilege": "Browse"
    }
  ],
  "ConnectionProfileManagement": [
    {
      "ControlmServer": "*",
      "Agent": "sparkit",
      "PluginType": "*",
      "Name": "${uc_user_code}*",
      "Privilege": "Full"
    },
    {
      "ControlmServer": "IN01",
      "Agent": "sparkit",
      "PluginType": "*",
      "Name": "SPARKIT*",
      "Privilege": "Browse"
    }
  ]
}
EOF
}

function Build_Agent_Resources {
  
  filename=$1
  
  cat > ${filename} <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: plugins-list
data:
  plugins_list.txt: |
    AAF112024
    AAFJEQ
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: mft-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 10Mi
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mft-config-params
data:
  com.bmc.aft.configurable.ftp.protocolJobOutputDebugLevel: "DEBUG"
  com.bmc.aft.configurable.printTransferDefinitions: "true"
EOF
}

function Build_SFTP_CCP {

  user_code=$1
  sftp_user=$2
  pk_name=$3  # no key passphrase
  hostname=$4
  filename=$5

  cat > ${filename} <<EOF
{
  "${user_code}_SFTP": {
    "Type": "ConnectionProfile:FileTransfer:SFTP",
    "VerifyBytes": true,
    "SSHCompression": false,
    "User": "${sftp_user}",
    "PrivateKeyName": "${pk_name}",
    "HostName": "${hostname}",
    "Description": "",
    "Centralized": true
  }
}
EOF
}


function Provision_Agents_Helm {

  ctm_user_code=$1        # Prefix used for Agent name and namespace
  ctm_aapi_endpoint=$2    # Control-M API URL
  ctm_auth_token=$3       # API Token
  ctm_server=$4           # Control-M Server Name
  resources_file=$5       # Agent resources filename
  ctm_hg=$6
  agent variable set CTM_HG "${ctm_hg}"

  helm repo add controlm https://controlm-charts.s3.us-west-2.amazonaws.com/
  helm repo update

  # Deploy agent resources to cluster
  kubectl create namespace ${ctm_user_code}
  kubectl apply -f ${resources_file} -n ${ctm_user_code}

  # Provision Control-M Agent with Helm
  helm upgrade --install ${ctm_user_code} controlm/helix-controlm-agent --version 9.22.000 \
    --set image.tag=9.22.000-k8s-mft-openjdk \
    --set-json 'pod.nodeSelector={"kubernetes.io/os":"linux"}' \
    --set-json 'pod.annotations={"cluster-autoscaler.kubernetes.io/safe-to-evict":"false"}' \
    --set server.name=${ctm_server} \
    --set api.endpoint=${ctm_aapi_endpoint} \
    --set api.token=${ctm_auth_token} \
    --set agent.tag=sparkit \
    --set pvc.storageClass=local-path \
    --set pvc.volumeSize=1Gi \
    --set pvc.accessMode=ReadWriteOnce \
    --set server.hostgroup=${ctm_hg} \
    --set ai.additionalPluginsConfigMapName=plugins-list \
    --set mft.pvcs[0].name=mft-pvc \
    --set mft.pvcs[0].mountPath=mft_mountPath \
    --set mft.configParametersConfigMapName=mft-config-params \
    --set mft.sshPrivateKeySecretName=airflow-id \
    --set mft.sshPrivateKeySecretName=k3s-sftp-key \
    --namespace=${ctm_user_code} --create-namespace

}

function Create_Docker_Secret {

  name=$1
  namespace=$2
  docker_config=$3

  echo "${docker_config}" > /tmp/docker_config.json
  secret_json=$(cat /tmp/docker_config.json | base64 -w 0)
  cat > /tmp/docker_secret.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: ${name}
  namespace: ${namespace}
data:
  .dockerconfigjson: ${secret_json}
type: kubernetes.io/dockerconfigjson
EOF

  kubectl apply -f /tmp/docker_secret.yaml
  rm /tmp/docker_secret.yaml
  rm /tmp/docker_config.json
}

function Install_PostgreSQL {

  namespace=$1
  secret_name=$2
  docker_config=$3
  
  if [[ -z "${PG_PASSWORD}" ]]; then
    echo "Error: Secret PG_PASSWORD not set!"
    exit 8
  fi
  Create_Docker_Secret ${secret_name} ${namespace} ${docker_config}
  helm install postgres bitnami/postgresql \
    --set auth.postgresPassword="${PG_PASSWORD}" \
    --set image.pullPolicy="IfNotPresent" \
    --set impagePullSecrets="${secret_name}" \
    -n ${namespace}
  export PG_CLUSTER_IP=$(kubectl -n ${namespace} get service postgres-postgresql -o json | jq -r '.spec.clusterIP')
  agent variable set PG_CLUSTER_IP ${PG_CLUSTER_IP}
  agent variable set PG_PASSWORD ${PG_PASSWORD}
  echo "${PG_CLUSTER_IP} ${PG_PASSWORD}" > /tmp/pg.txt

}

function Create_SFTP_Key {

  key_name=$1

  ssh_dir="/root/.ssh"
  key_path="${ssh_dir}/${key_name}"
  key_comment="sftp-user@example.com"
  ssh-keygen -t ed25519 -f "${key_path}" -q -N "" -C "$key_comment"
  chmod 600 "${key_path}"
  cat "${key_path}.pub" >> "${ssh_dir}/authorized_keys"
  sftp_key=$(cat ${key_path})

}

function Setup_for_Airflow {

  # Capture and set airflow vm ip to be used in a challenge for MFT Connectin Profile
  #AIRFLOW_IP=$(nslookup airflow3 |grep Address | tail -n 1 | cut -d' ' -f2)
  agent variable set AIRFLOW_IP "${HOSTNAME}"
  K3S_IP=$(nslookup kubernetes-vm |grep Address | tail -n 1 | cut -d' ' -f2)
  agent variable set KUBERNETES_IP "${K3S_IP}"
  airflow_password=$(jq -r '.admin' /root/airflow/simple_auth_manager_passwords.json.generated)
  agent variable set AIRFLOW_PASSWORD ${airflow_password}
  agent variable set AIRFLOW_USER "admin"
  
  # Adding Kubernetes Agent(s)
  Build_Agent_Resources "/root/ctm_agent_resources.yaml"
  Provision_Agents_Helm ${CTM_USER_CODE} ${CTM_AAPI_ENDPOINT} ${CTM_AUTH_TOKEN} IN01 "/root/ctm_agent_resources.yaml" ${CTM_HG}
  kubectl create secret generic airflow-id --from-file=/root/airflow_id --namespace ${CTM_USER_CODE}
  Create_SFTP_Key "k3s-sftp-key"
  kubectl create secret generic k3s-sftp-key --from-file=/root/.ssh/k3s-sftp-key --namespace ${CTM_USER_CODE}
  Install_PostgreSQL ${CTM_USER_CODE} "regcred" ${DOCKER_CONFIG}
  Build_SFTP_CCP "${CTM_USER_CODE^^}" "root" "k3s-sftp-key" "${K3S_IP}" "/root/${CTM_USER_CODE}_sftp_cp.json"
  ctm deploy "/root/${CTM_USER_CODE}_sftp_cp.json"

  # Copying the scripts to Airflow directories
  cp /root/labs/whiskey-retail/dags/*.py /root/airflow/dags/
  mkdir -p /root/airflow/scripts
  envsubst < /root/labs/whiskey-retail/scripts/analyze_data.py > /root/scripts/analyze_data.py
  cp /root/labs/whiskey-retail/scripts/analyze_wrapper.sh /root/scripts/
  cp /root/labs/whiskey-retail/scripts/analyze_whiskey_data.sh /root/scripts/
  chmod +x /root/scripts/analyze_whiskey_data.sh
  chmod +x /root/scripts/analyze_wrapper.sh
  envsubst < /root/labs/whiskey-retail/scripts/analyze_whiskey_data.py > /root/airflow/dags/analyze_whiskey_data.py

}

function Clone_Repo_Folder {
  
  repo_name=$1
  repo_alias=$2
  repo_folder=$3
  target_folder=$4

  git clone --filter blob:none --sparse ${repo_alias}:${repo_name} ${target_folder}
  cd ${target_folder}
  git sparse-checkout set ${repo_folder}

}

function Clone_Repo {

  repo_name=$1
  repo_alias=$2
  target_folder=$3

  git clone ${repo_alias}:${repo_name} ${target_folder}

}

function Run_Background_Script {

  # The script_file (absolute path) must exist on VM and set executable
  script_file=$1
  arguments=$2

  chmod +x ${script_file}
  nohup /bin/sh -c "${script_file} ${arguments}" &

}

function Configure_CTM_User {
  ctm_user_code=$1
  ctm_uc_user_code=${ctm_user_code^^}
  ctm_user=$2
  ctm_tst_role=$3
  ctm_tst_token=$4
  
  # Start CTM Provisioning
  if [ "${MODE}" == "INVITE" ]; then
      Build_Role_Template ${ctm_user_code} ${ctm_uc_user_code}
      Build_User_Template ${ctm_user_code} ${ctm_user}
      Build_Token_Template ${ctm_user_code}
      Create_TD_Role ${ctm_user_code} 
      Create_TD_User ${ctm_user} ${ctm_user_code}
      Create_TD_Token ${ctm_user_code}
  else
      # Its expected the test role and api token already exist in target environment
      ctm config authorization:role::get ${ctm_tst_role}
      if [ "$?" -ne "0" ]; then
          echo "Error: Test Role ${ctm_tst_role} does not exist"
          exit 8
      fi
      ctm authentication token::get ${ctm_tst_role}
      if [ "$?" -ne "0" ]; then
          echo "Error: Test API Token ${ctm_tst_token} does not exist"
          exit 8
      fi
      # Just building the templates for debugging purposes
      Build_Role_Template ${ctm_user_code} ${ctm_uc_user_code}
      Build_User_Template ${ctm_user_code} ${ctm_user}
      Build_Token_Template ${ctm_user_code}
  fi

}

function Install_AAPI {

  ctm_cli_url=$1

  cd ~
  curl -O curl -O ${ctm_cli_url}
  
  # Extract the filename from url
  regex="([^/]*)$"
  if [[ "${ctm_cli_url}" =~ $"{regex}" ]]; then
    filename="${BASH_REMATCH[1]}"
    echo "The file extension is: $extension"
  fi
  
  python3 -m venv venv
  source venv/bin/activate
  python ${filename}

}

function Add_AAPI_Env {

  ctm_env=$1
  ctm_aapi_endpoint=$2
  ctm_aapi_token=$3

  ctm env saas::add ${ctm_env} ${ctm_aapi_endpoint} ${ctm_aapi_token}

}

#=====================
# Check_Mode_Vars
#====================
# Arguments:
#  None
# Outputs
#  MODE = INVITE | TEST
# Comments:
#  Tests whether the Track was started using an Invite or in Test mode.
#=====================
# Set_User_Data
#====================
# Arguments
# - gen_random_code - A value of "random" will generate a random value for CTM_USER_CODE.  Otherwise uses the First and Last name.
# Outputs
#  
# Comments
#  Sets User Data for the Track
