
#!/usr/bin/env bash


# Require a binary on PATH
requires() { command -v "$1" >/dev/null 2>&1 || { echo "Error: '$1' not found." >&2; return 127; }; }

# Idempotent namespace ensure
ns_ensure() {
  local ns="${1:?usage: ns_ensure <namespace>}"
  kubectl get ns "${ns}" >/dev/null 2>&1 || kubectl create ns "${ns}"
}

# Optional agent setter
agent_set() { command -v agent >/dev/null 2>&1 && agent variable set "$@"; }


function Create_Local_User {
  local user="${1:?usage: Create_Local_User <user> <group> <home_dir>}"
  local group="${2:?usage: Create_Local_User <user> <group> <home_dir>}"
  local home_dir="${3:?usage: Create_Local_User <user> <group> <home_dir>}"

  if ! getent group "${group}" >/dev/null; then
    groupadd --force "${group}"
  fi

  if ! id -u "${user}" &>/dev/null; then
    useradd -m -d "${home_dir}" -g "${group}" -s /bin/bash "${user}"
  fi

  chown -R "${user}:${group}" "${home_dir}"
}

function Check_Mode_Vars {
  [[ -z "${CTM_AAPI_ENDPOINT:-}" ]] && echo "Warning: env variable CTM_AAPI_ENDPOINT not set!"
  [[ -z "${CTM_PRV_ENV:-}"       ]] && echo "Warning: env variable CTM_PRV_ENV not set!"
  [[ -z "${CTM_USER_ENV:-}"      ]] && echo "Warning: env variable CTM_USER_ENV not set!"
  [[ -z "${CTM_PRV_TOKEN:-}"     ]] && echo "Warning: env variable CTM_PRV_TOKEN not set!"

  if [[ -z "${INSTRUQT_USER_EMAIL:-}" ]]; then
    export MODE="TEST"
    if [[ -z "${CTM_TST_TOKEN:-}" ]]; then
      echo "Warning: env variable CTM_TST_TOKEN not set!"
    else
      export CTM_AUTH_TOKEN="${CTM_TST_TOKEN}"
    fi
    [[ -z "${CTM_TST_ROLE:-}" ]] && echo "Warning: env variable CTM_TST_ROLE not set!"
  else
    export MODE="INVITE"
  fi

  if command -v agent >/dev/null 2>&1; then
    agent variable set MODE "${MODE}"
  fi
}

function Set_User_Data {
  local gen_random_code="${1:-}"
  local current_mode="${MODE:-TEST}"

  if [[ "${current_mode}" == "INVITE" ]]; then
    export CTM_USER_NAME="${INSTRUQT_USER_NAME:?INSTRUQT_USER_NAME required in INVITE mode}"
    export CTM_USER="${INSTRUQT_USER_EMAIL:?INSTRUQT_USER_EMAIL required in INVITE mode}"

    local first_name="" last_name=""
    read -r first_name last_name <<< "${INSTRUQT_USER_NAME}"
    if [[ -z "${last_name}" ]]; then
      echo "Error: Please provide both a first and last name in INSTRUQT_USER_NAME." >&2
      return 2
    fi

    if [[ "${gen_random_code}" == "random_code" ]]; then
      export CTM_USER_CODE
      CTM_USER_CODE="$(Generate_User_Code)"
    else
      local first_initial="${first_name:0:1}"
      local last_initials="${last_name:0:2}"
      local random_digit="$((RANDOM % 10))"
      export CTM_USER_CODE
      CTM_USER_CODE="$(echo "${first_initial}${last_initials}${random_digit}" | tr '[:upper:]' '[:lower:]')"
    fi
  else
    export CTM_USER="tst-inst@example.com"
    export CTM_USER_NAME="Test User"
    export CTM_USER_CODE="tus"
  fi

  export CTM_UC_USER_CODE="${CTM_USER_CODE^^}"

  if command -v agent >/dev/null 2>&1; then
    agent variable set CTM_USER         "${CTM_USER}"
    agent variable set CTM_USER_NAME    "${CTM_USER_NAME}"
    agent variable set CTM_USER_CODE    "${CTM_USER_CODE}"
    agent variable set CTM_UC_USER_CODE "${CTM_UC_USER_CODE}"
  fi

  cat <<EOF
============================================
Mode: ${MODE:-TEST}
AAPI Endpoint: ${CTM_AAPI_ENDPOINT:-<unset>}
CTM User: ${CTM_USER}
CTM User Name: ${CTM_USER_NAME}
User Code: ${CTM_USER_CODE}
============================================
EOF
}

function Generate_User_Code {
  local alpha numeric
  alpha="$(tr -dc 'a-z' </dev/urandom | head -c 3)"
  numeric="$(tr -dc '0-9' </dev/urandom | head -c 1)"
  echo "${alpha}${numeric}"
}


function Setup_GH_PK {
  local private_key="${1:?usage: Setup_GH_PK <private_key> <pk_filename> <known_hosts> <repo_alias>}"
  local pk_filename="${2:?usage: Setup_GH_PK <private_key> <pk_filename> <known_hosts> <repo_alias>}"
  local known_hosts="${3:?usage: Setup_GH_PK <private_key> <pk_filename> <known_hosts> <repo_alias>}"
  local repo_alias="${4:?usage: Setup_GH_PK <private_key> <pk_filename> <known_hosts> <repo_alias>}"

  local ssh_dir
  ssh_dir="${HOME}/.ssh"

  # Ensure ~/.ssh exists with strict permissions
  mkdir -p "${ssh_dir}"
  chmod 700 "${ssh_dir}"

  # Write private key (idempotent overwrite) with strict perms
  printf '%s\n' "${private_key}" > "${ssh_dir}/${pk_filename}"
  chmod 400 "${ssh_dir}/${pk_filename}"

  # Append known_hosts only if the host key line(s) aren’t present
  if ! grep -Fq "$(printf '%s' "${known_hosts}" | awk '{print $1}')" "${ssh_dir}/known_hosts" 2>/dev/null; then
    printf '%s\n' "${known_hosts}" >> "${ssh_dir}/known_hosts"
  fi
  chmod 644 "${ssh_dir}/known_hosts"

  # Add a host stanza if missing (idempotent)
  local cfg_block
  cfg_block=$(
    cat <<EOF
Host ${repo_alias}
  HostName github.com
  User git
  IdentityFile ${ssh_dir}/${pk_filename}
EOF
  )

  touch "${ssh_dir}/config"
  chmod 600 "${ssh_dir}/config"
  if ! grep -Fq "Host ${repo_alias}" "${ssh_dir}/config"; then
    printf '\n%s\n' "${cfg_block}" >> "${ssh_dir}/config"
  fi
}


function Create_TD_Role {
  local user_code="${1:?usage: Create_TD_Role <user_code>}"

  # Tool checks
  command -v ctm       >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }
  command -v envsubst >/dev/null 2>&1 || { echo "Error: 'envsubst' not found."   >&2; return 127; }

  # Prepare template substitution (provide vars only to envsubst)
  local uc_user_code
  uc_user_code="${user_code^^}"

  user_code="${user_code}" uc_user_code="${uc_user_code}" \
    envsubst < /tmp/role_template_file.json > /tmp/role_def_sub.json

  # Check existence via CLI exit status or via filtered output
  if ctm config authorization:roles::get -s "role=${user_code}" >/dev/null 2>&1; then
    echo "Role '${user_code}' already exists."
  else
    echo "Creating role '${user_code}'"
    ctm config authorization:role::add /tmp/role_def_sub.json
  fi
}


function Create_TD_User {
  local user="${1:?usage: Create_TD_User <user> <user_code>}"
  local user_code="${2:?usage: Create_TD_User <user> <user_code>}"

  command -v ctm       >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }
  command -v jq        >/dev/null 2>&1 || { echo "Error: 'jq' not found."        >&2; return 127; }
  command -v envsubst >/dev/null 2>&1 || { echo "Error: 'envsubst' not found."   >&2; return 127; }

  # Does the user exist?
  if ctm config authorization:user::get "${user}" >/dev/null 2>&1; then
    echo "User '${user}' already exists; ensuring role '${user_code}' is present."

    # Fetch user JSON, add role if missing (create Roles array if absent), then update
    ctm config authorization:user::get "${user}" \
      | jq --arg role "${user_code}" '
          .Roles = (
            ( .Roles // [] )
            | (index($role) // -1) as $i
            | if $i == -1 then . + [$role] else . end
          )
        ' > /tmp/user_def_upd.json

    ctm config authorization:user::update "${user}" /tmp/user_def_upd.json
  else
    # Create new user via templated JSON
    user="${user}" user_code="${user_code}" \
      envsubst < /tmp/user_template_file.json > /tmp/user_def_sub.json

    echo "Adding user '${user}' using /tmp/user_def_sub.json"
    ctm config authorization:user::add /tmp/user_def_sub.json
  fi
}


function Create_TD_Token {
  # Ensure required tools exist
  command -v ctm >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }
  command -v jq  >/dev/null 2>&1 || { echo "Error: 'jq' not found."       >&2; return 127; }

  # Build template must exist
  if [[ ! -s /tmp/token_template_file.json ]]; then
    echo "Error: /tmp/token_template_file.json not found or empty." >&2
    return 2
  fi

  # Create token; catch failures without breaking the whole script
  local token
  if ! token="$(ctm authentication token::create -f /tmp/token_template_file.json 2>/dev/null | jq -r '.tokenValue')"; then
    echo "Failed to create CTM authentication token (ctm/jq error)." >&2
    return 1
  fi

  if [[ -n "${token}" && "${token}" != "null" ]]; then
    export CTM_AUTH_TOKEN="${token}"
    # Set agent variable if available
    if command -v agent >/dev/null 2>&1; then
      agent variable set CTM_AUTH_TOKEN "${CTM_AUTH_TOKEN}" || true
    fi
    echo "CTM_AUTH_TOKEN successfully created and exported."
  else
    echo "Failed to create CTM authentication token (empty/null tokenValue)." >&2
    return 1
  fi
}

function Build_User_Template {
  local user_code="${1:?usage: Build_User_Template <user_code> <user_email>}"
  local user="${2:?usage: Build_User_Template <user_code> <user_email>}"

  # Write minimal template; assume user and user_code contain no double-quotes.
  # If user/email may contain quotes, add an escaping helper.
  cat > /tmp/user_template_file.json <<EOF
{
  "Name": "${user}",
  "Roles": [
    "${user_code}"
  ]
}
EOF
}

function Build_Token_Template {
  local user_code="${1:?usage: Build_Token_Template <user_code>}"

  cat > /tmp/token_template_file.json <<EOF
{
  "tokenName": "${user_code}",
  "Roles": [
    "${user_code}"
  ]
}
EOF


function Build_Role_Template {
  local user_code="${1:?usage: Build_Role_Template <user_code> <uc_user_code>}"
  local uc_user_code="${2:?usage: Build_Role_Template <user_code> <uc_user_code>}"

  # Write template with placeholders for envsubst
  # IMPORTANT: We use upper-case names to match env vars in Create_TD_Role
  local tmp="/tmp/role_template_file.json.tmp"
  cat > "${tmp}" <<EOF
{
  "Name": "\${user_code}",
  "AllowedJobs": {
    "Included": [
      [
        [
          "Folder",
          "like",
          "\${user_code}*"
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
      "ApplicationIntegratorAccess": "Full",
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
      "Folder": "\${user_code}*",
      "Run": true
    }
  ],
  "RunasUsers": [
    {
      "ControlmServer": "*",
      "RunasUser": "*",
      "Host": "\${user_code}*"
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
      "Name": "\${user_code}*"
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
      "Name": "\${uc_user_code}*",
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
  mv "${tmp}" /tmp/role_template_file.json
}


function Build_Agent_Resources {
  local filename="${1:?usage: Build_Agent_Resources <filename>}"

  local tmp="${filename}.tmp"
  cat > "${tmp}" <<'EOF'
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
  mv "${tmp}" "${filename}"
}


function Build_SFTP_CCP {
  local user_code="${1:?usage: Build_SFTP_CCP <user_code> <sftp_user> <pk_name> <hostname> <filename>}"
  local sftp_user="${2:?usage: Build_SFTP_CCP <user_code> <sftp_user> <pk_name> <hostname> <filename>}"
  local pk_name="${3:?usage: Build_SFTP_CCP <user_code> <sftp_user> <pk_name> <hostname> <filename>}"
  local hostname="${4:?usage: Build_SFTP_CCP <user_code> <sftp_user> <pk_name> <hostname> <filename>}"
  local filename="${5:?usage: Build_SFTP_CCP <user_code> <sftp_user> <pk_name> <hostname> <filename>}"

  local tmp="${filename}.tmp"
  cat > "${tmp}" <<EOF
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
  mv "${tmp}" "${filename}"
}

function Provision_Agents_Helm {
  local ctm_user_code="${1:?usage: Provision_Agents_Helm <ctm_user_code> <aapi_endpoint> <auth_token> <ctm_server> <resources_file> <ctm_hg>}"
  local ctm_aapi_endpoint="${2:?usage: Provision_Agents_Helm <ctm_user_code> <aapi_endpoint> <auth_token> <ctm_server> <resources_file> <ctm_hg>}"
  local ctm_auth_token="${3:?usage: Provision_Agents_Helm <ctm_user_code> <aapi_endpoint> <auth_token> <ctm_server> <resources_file> <ctm_hg>}"
  local ctm_server="${4:?usage: Provision_Agents_Helm <ctm_user_code> <aapi_endpoint> <auth_token> <ctm_server> <resources_file> <ctm_hg>}"
  local resources_file="${5:?usage: Provision_Agents_Helm <ctm_user_code> <aapi_endpoint> <auth_token> <ctm_server> <resources_file> <ctm_hg>}"
  local ctm_hg="${6:?usage: Provision_Agents_Helm <ctm_user_code> <aapi_endpoint> <auth_token> <ctm_server> <resources_file> <ctm_hg>}"

  requires helm || return $?
  requires kubectl || return $?

  agent_set CTM_HG "${ctm_hg}"

  # Helm repo setup (idempotent)
  helm repo add controlm "https://controlm-charts.s3.us-west-2.amazonaws.com/" >/dev/null 2>&1 || true
  helm repo update

  # Ensure namespace exists; apply resources
  ns_ensure "${ctm_user_code}"
  [[ -s "${resources_file}" ]] || { echo "Error: resources_file '${resources_file}' not found or empty." >&2; return 2; }
  kubectl apply -f "${resources_file}" -n "${ctm_user_code}"

  # NOTE: Avoid duplicate flags; set each value once.
  # TIP: The mft mountPath should be an absolute path (e.g., /opt/controlm/mft). Adjust as needed.
  helm upgrade --install "${ctm_user_code}" controlm/helix-controlm-agent --version "9.22.000" \
    --set image.tag="9.22.000-k8s-mft-openjdk" \
    --set-json 'pod.nodeSelector={"kubernetes.io/os":"linux"}' \
    --set-json 'pod.annotations={"cluster-autoscaler.kubernetes.io/safe-to-evict":"false"}' \
    --set server.name="${ctm_server}" \
    --set api.endpoint="${ctm_aapi_endpoint}" \
    --set api.token="${ctm_auth_token}" \
    --set agent.tag="sparkit" \
    --set pvc.storageClass="local-path" \
    --set pvc.volumeSize="1Gi" \
    --set pvc.accessMode="ReadWriteOnce" \
    --set server.hostgroup="${ctm_hg}" \
    --set ai.additionalPluginsConfigMapName="plugins-list" \
    --set mft.pvcs[0].name="mft-pvc" \
    --set mft.pvcs[0].mountPath="/mft_mountPath" \
    --set mft.configParametersConfigMapName="mft-config-params" \
    --set mft.sshPrivateKeySecretName="k3s-sftp-key" \
    --namespace "${ctm_user_code}" --create-namespace
}

function Create_Docker_Secret {
  local name="${1:?usage: Create_Docker_Secret <name> <namespace> <docker_config_json>}"
  local namespace="${2:?usage: Create_Docker_Secret <name> <namespace> <docker_config_json>}"
  local docker_config="${3:?usage: Create_Docker_Secret <name> <namespace> <docker_config_json>}"

  requires kubectl || return $?

  # Build secret YAML (portable base64: -w 0 on GNU; fallback to strip newlines)
  printf '%s\n' "${docker_config}" > /tmp/docker_config.json
  local secret_json
  if base64 -w 0 </tmp/docker_config.json >/dev/null 2>&1; then
    secret_json="$(base64 -w 0 </tmp/docker_config.json)"
  else
    secret_json="$(base64 </tmp/docker_config.json | tr -d '\n')"
  fi

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
  rm -f /tmp/docker_secret.yaml /tmp/docker_config.json
}

function Install_PostgreSQL {
  local namespace="${1:?usage: Install_PostgreSQL <namespace> <secret_name> <docker_config_json>}"
  local secret_name="${2:?usage: Install_PostgreSQL <namespace> <secret_name> <docker_config_json>}"
  local docker_config="${3:?usage: Install_PostgreSQL <namespace> <secret_name> <docker_config_json>}"

  requires helm || return $?
  requires kubectl || return $?
  requires jq || return $?

  if [[ -z "${PG_PASSWORD:-}" ]]; then
    echo "Error: Secret PG_PASSWORD not set!" >&2
    return 8
  fi

  # Registry pull secret (idempotent apply)
  Create_Docker_Secret "${secret_name}" "${namespace}" "${docker_config}"

  # NOTE: Bitnami charts use 'global.imagePullSecrets'; you had a typo.
  # Depending on chart version, you may also use 'image.pullSecrets[0]=<name>'.
  helm install postgres bitnami/postgresql \
    --set auth.postgresPassword="${PG_PASSWORD}" \
    --set image.pullPolicy="IfNotPresent" \
    --set global.imagePullSecrets[0]="${secret_name}" \
    -n "${namespace}"

  # Capture service ClusterIP
  local pg_ip
  pg_ip="$(kubectl -n "${namespace}" get service postgres-postgresql -o json | jq -r '.spec.clusterIP')"
  if [[ -z "${pg_ip}" || "${pg_ip}" == "null" ]]; then
    echo "Warning: Could not resolve PostgreSQL ClusterIP." >&2
    return 1
  fi

  export PG_CLUSTER_IP="${pg_ip}"
  agent_set PG_CLUSTER_IP "${PG_CLUSTER_IP}"
  agent_set PG_PASSWORD "${PG_PASSWORD}"
  printf '%s %s\n' "${PG_CLUSTER_IP}" "${PG_PASSWORD}" > /tmp/pg.txt
}

function Create_SFTP_Key {
  local key_name="${1:?usage: Create_SFTP_Key <key_name> <ssh_dir>}"
  local ssh_dir="${2:?usage: Create_SFTP_Key <key_name> <ssh_dir>}"

  local key_path="${ssh_dir}/${key_name}"
  local key_comment="sftp-user@example.com"

  # Ensure ~/.ssh exists with strict perms
  mkdir -p "${ssh_dir}"
  chmod 700 "${ssh_dir}"

  # Generate ED25519 key silently if it doesn't already exist
  if [[ ! -f "${key_path}" ]]; then
    ssh-keygen -t ed25519 -f "${key_path}" -q -N "" -C "${key_comment}"
  fi
  chmod 600 "${key_path}"

  # Append pubkey to authorized_keys if missing (idempotent)
  local pub_line
  pub_line="$(cat "${key_path}.pub")"
  touch "${ssh_dir}/authorized_keys"
  chmod 600 "${ssh_dir}/authorized_keys"
  grep -Fqx -- "${pub_line}" "${ssh_dir}/authorized_keys" || printf '%s\n' "${pub_line}" >> "${ssh_dir}/authorized_keys"

  # Expose the private key content to caller if needed
  # (Export a variable or echo; choose one. Here we echo to stdout.)
  cat "${key_path}"
}

function Clone_Repo_Folder {
  local repo_name="${1:?usage: Clone_Repo_Folder <repo_name> <repo_alias> <repo_folder> <target_folder>}"
  local repo_alias="${2:?usage: Clone_Repo_Folder <repo_name> <repo_alias> <repo_folder> <target_folder>}"
  local repo_folder="${3:?usage: Clone_Repo_Folder <repo_name> <repo_alias> <repo_folder> <target_folder>}"
  local target_folder="${4:?usage: Clone_Repo_Folder <repo_name> <repo_alias> <repo_folder> <target_folder>}"

  requires git || return $?

  # Clone as sparse, minimal history
  git clone --filter=blob:none --sparse --depth 1 "${repo_alias}:${repo_name}" "${target_folder}"
  (
    cd "${target_folder}" || { echo "Error: cannot cd to ${target_folder}" >&2; return 2; }
    git sparse-checkout set --cone "${repo_folder}"
    # Ensure the folder exists after sparse selection
    [[ -d "${repo_folder}" ]] || { echo "Error: repo folder '${repo_folder}' not found after sparse-checkout." >&2; return 3; }
  )
}

function Clone_Repo {
  local repo_name="${1:?usage: Clone_Repo <repo_name> <repo_alias> <target_parent_folder>}"
  local repo_alias="${2:?usage: Clone_Repo <repo_name> <repo_alias> <target_parent_folder>}"
  local target_parent="${3:?usage: Clone_Repo <repo_name> <repo_alias> <target_parent_folder>}"

  requires git || return $?

  mkdir -p "${target_parent}"
  (
    cd "${target_parent}" || { echo "Error: cannot cd to ${target_parent}" >&2; return 2; }
    git clone "${repo_alias}:${repo_name}"
  )
}

function Run_Background_Script {
  local script_file="${1:?usage: Run_Background_Script <script_file> <arguments>}"
  local arguments="${2:-}"  # optional

  [[ -x "${script_file}" ]] || chmod +x "${script_file}"

  # Use full paths for logs; capture PID
  local log_file
  log_file="$(dirname "${script_file}")/output.log"

  nohup /bin/sh -c "\"${script_file}\" ${arguments}" > "${log_file}" 2>&1 &
  echo $! > "$(dirname "${script_file}")/script.pid"
}

function Run_Background_As_User {
  local script_file="${1:?usage: Run_Background_As_User <script_file> <arguments> <user>}"
  local arguments="${2:-}"  # optional
  local user="${3:?usage: Run_Background_As_User <script_file> <arguments> <user>}"

  [[ -x "${script_file}" ]] || chmod +x "${script_file}"

  local log_file
  log_file="$(dirname "${script_file}")/output.log"
  local pid_file
  pid_file="$(dirname "${script_file}")/script.pid"

  # su - user -c 'nohup sh -c "<script> args" >log 2>&1 &'
  # Important: we single-quote the overall command and escape inner quotes.
  su - ${user} -c nohup /bin/sh -c "${script_file} ${arguments}" > output.log 2>&1 &
}


function Configure_CTM_User {
  local ctm_user_code="${1:?usage: Configure_CTM_User <ctm_user_code> <ctm_user> <ctm_tst_role> <ctm_tst_token>}"
  local ctm_uc_user_code="${ctm_user_code^^}"
  local ctm_user="${2:?usage: Configure_CTM_User <ctm_user_code> <ctm_user> <ctm_tst_role> <ctm_tst_token>}"
  local ctm_tst_role="${3:-}"   # only used in TEST mode
  local ctm_tst_token="${4:-}" # only used in TEST mode

  # Tool checks
  command -v ctm       >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }

  if [[ "${MODE:-TEST}" == "INVITE" ]]; then
    Build_Role_Template  "${ctm_user_code}" "${ctm_uc_user_code}"
    Build_User_Template  "${ctm_user_code}" "${ctm_user}"
    Build_Token_Template "${ctm_user_code}"
    Create_TD_Role       "${ctm_user_code}"
    Create_TD_User       "${ctm_user}" "${ctm_user_code}"
    Create_TD_Token      "${ctm_user_code}"
  else
    # Validate role exists
    if ctm config authorization:role::get "${ctm_tst_role}" >/dev/null 2>&1; then
      :
    else
      echo "Error: Test Role '${ctm_tst_role}' does not exist." >&2
      return 8
    fi
    # Validate token exists
    if ctm authentication token::get "${ctm_tst_token}" >/dev/null 2>&1; then
      :
    else
      echo "Error: Test API Token '${ctm_tst_token}' does not exist." >&2
      return 8
    fi
    # Build templates for debugging consistency
    Build_Role_Template  "${ctm_user_code}" "${ctm_uc_user_code}"
    Build_User_Template  "${ctm_user_code}" "${ctm_user}"
    Build_Token_Template "${ctm_user_code}"
  fi
}


function Install_AAPI {
  local ctm_cli_url="${1:?usage: Install_AAPI <ctm_cli_url> <install_dir>}"
  local install_dir="${2:?usage: Install_AAPI <ctm_cli_url> <install_dir>}"

  command -v curl    >/dev/null 2>&1 || { echo "Error: 'curl' not found."    >&2; return 127; }
  command -v python3 >/dev/null 2>&1 || { echo "Error: 'python3' not found." >&2; return 127; }

  mkdir -p "${install_dir}"
  (
    cd "${install_dir}" || { echo "Error: cannot cd to '${install_dir}'." >&2; return 2; }
    curl -fLO --retry 3 --retry-delay 2 "${ctm_cli_url}"

    local filename
    filename="$(basename -- "${ctm_cli_url}")"
    echo "ctm_cli_url filename is ${filename}"

    python3 -m venv venv
    # shellcheck disable=SC1091
    source "venv/bin/activate"
    python3 "${filename}"
  )
}


function Add_AAPI_Env {
  local ctm_env="${1:?usage: Add_AAPI_Env <env_name> <aapi_endpoint> <aapi_token>}"
  local ctm_aapi_endpoint="${2:?usage: Add_AAPI_Env <env_name> <aapi_endpoint> <aapi_token>}"
  local ctm_aapi_token="${3:?usage: Add_AAPI_Env <env_name> <aapi_endpoint> <aapi_token>}"

  command -v ctm >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }

  if ! ctm env saas::add "${ctm_env}" "${ctm_aapi_endpoint}" "${ctm_aapi_token}"; then
    echo "Error: failed to add AAPI env '${ctm_env}'." >&2
    return 1
  fi
}


function Set_Hostname {
  local new_hostname="${1:?usage: Set_Hostname <new_hostname>}"
  command -v hostnamectl >/dev/null 2>&1 || { echo "Error: 'hostnamectl' not found." >&2; return 127; }

  if ! hostnamectl set-hostname "${new_hostname}"; then
    echo "Error: failed to set hostname to ${new_hostname}." >&2
    return 1
  fi
}

function Repo_Replacements {
  local repo_dir="${1:?usage: Repo_Replacements <repo_dir> <space_delimited_replacements>}"
  local replacements="${2:?usage: Repo_Replacements <repo_dir> <space_delimited_replacements>}"

  # Ensure the directory exists
  [[ -d "${repo_dir}" ]] || { echo "Error: repo_dir '${repo_dir}' not found." >&2; return 2; }

  # Split the single, quoted, space-delimited argument into an array of tokens
  # Example input: "foo=bar IN01=IN02 SPARKIT-HG=SPARKIT-HG-NEW"
  local tokens=()
  # shellcheck disable=SC2206  # intentional word splitting on spaces
  tokens=( ${replacements} )

  if (( ${#tokens[@]} == 0 )); then
    echo "Warning: No replacements specified." >&2
    return 0
  fi

  local delimiter="="
  local token find_str repl_str

  for token in "${tokens[@]}"; do
    # Split on first '='
    find_str="${token%%${delimiter}*}"
    repl_str="${token#*${delimiter}}"

    if [[ -z "${find_str}" ]]; then
      echo "Warning: empty find_str in token '${token}', skipping." >&2
      continue
    fi
    # If token had no '=', repl_str will be identical to token; treat that as malformed.
    if [[ "${find_str}" == "${repl_str}" ]]; then
      echo "Warning: malformed token '${token}', skipping." >&2
      continue
    fi

    echo "Replacing '${find_str}' → '${repl_str}' under '${repo_dir}/'..."

    # Perform in-place replacement across regular files; use '|' as sed delimiter to reduce escaping needs.
    # Note: if find_str contains '|' you should escape it (see note below).
    LC_ALL=C find "${repo_dir}/" -type f -print0 \
      | xargs -0 sed -i "s|${find_str}|${repl_str}|g"

    echo "Done: '${find_str}' → '${repl_str}'."
  done
}

function Config_Code_Server {
  local user_home="${1:?usage: Config_Code_Server <user_home> <base_dir> <user>}"
  local base_dir="${2:?usage: Config_Code_Server <user_home> <base_dir> <user>}"
  local user="${3:?usage: Config_Code_Server <user_home> <base_dir> <user>}"

  # Ensure code-server is available (fail fast if missing)
  command -v code-server >/dev/null 2>&1 || { echo "Error: 'code-server' not found on PATH." >&2; return 127; }

  # Install VS Code extensions for the specified user
  # su - <user> -c 'code-server --install-extension <ext>'
  if ! su - "${user}" -c 'code-server --install-extension ms-python.python'; then
    echo "Error: failed to install ms-python.python for user '${user}'." >&2
    return 1
  fi
  if ! su - "${user}" -c 'code-server --install-extension ms-toolsai.jupyter'; then
    echo "Error: failed to install ms-toolsai.jupyter for user '${user}'." >&2
    return 1
  fi
  if ! su - "${user}" -c 'code-server --install-extension wesbos.theme-cobalt2'; then
    echo "Error: failed to install wesbos.theme-cobalt2 for user '${user}'." >&2
    return 1
  fi

  # Ensure settings directory exists, then set theme
  local settings_dir="${user_home}/.local/share/code-server/User"
  mkdir -p "${settings_dir}"
  printf '%s\n' '{"workbench.colorTheme": "Cobalt2"}' > "${settings_dir}/settings.json"

  # Add venv to .gitignore in the repo root (optional)
  local repo_root="${user_home}/${base_dir}"
  if [[ -d "${repo_root}" ]]; then
    # Create .gitignore if missing; append 'venv' only if not present
    local gitignore="${repo_root}/.gitignore"
    touch "${gitignore}"
    grep -Fxq 'venv' "${gitignore}" || echo 'venv' >> "${gitignore}"
  else
    echo "Warning: repo directory '${repo_root}' not found; skipping .gitignore update." >&2
  fi
}

