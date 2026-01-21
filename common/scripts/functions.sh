
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
  echo "End of Check_Mode_Vars"
}

function Set_User_Data {
  local gen_random_code="${1:-}"
  local current_mode="INVITE"

  if [ -z "${INSTRUQT_USER_NAME:-}" ]; then
    INSTRUQT_USER_NAME="Test User"
  fi
  if [ -z "${INSTRUQT_USER_EMAIL:-}" ]; then
    INSTRUQT_USER_EMAIL="tst-inst@example.com"
  fi

  if [[ "${current_mode}" == "INVITE" ]]; then
    export CTM_USER_NAME="${INSTRUQT_USER_NAME:?INSTRUQT_USER_NAME required in INVITE mode}"
    export CTM_USER="${INSTRUQT_USER_EMAIL:?INSTRUQT_USER_EMAIL required in INVITE mode}"

    OIFS="$IFS"
    IFS=' '
    local first_name="" last_name=""
    read -r first_name last_name <<< "${INSTRUQT_USER_NAME}"
    IFS="$OIFS"
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
  
  agent variable set CTM_USER         "${CTM_USER}"
  agent variable set CTM_USER_NAME    "${CTM_USER_NAME}"
  agent variable set CTM_USER_CODE    "${CTM_USER_CODE}"
  agent variable set CTM_UC_USER_CODE "${CTM_UC_USER_CODE}"
  

  cat <<EOF
============================================
Mode: ${MODE}
AAPI Endpoint: ${CTM_AAPI_ENDPOINT:-<unset>}
CTM User: ${CTM_USER}
CTM User Name: ${CTM_USER_NAME}
User Code: ${CTM_USER_CODE}
============================================
EOF
}

function Generate_User_Code {
  local alpha numeric
  alpha=$(head /dev/urandom | tr -dc a-z | head -c 3)
  numeric=$(head /dev/urandom | tr -dc 0-9 | head -c 1)
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
  local template_file=$2
  local build_file=/tmp/role_build_file.json

  # Tool checks
  command -v ctm       >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }
  command -v envsubst >/dev/null 2>&1 || { echo "Error: 'envsubst' not found."   >&2; return 127; }

  user_code="${user_code}" uc_user_code="${user_code^^}" \
    envsubst < ${template_file} > ${build_file}
  cat ${template_file}
  cat ${build_file}
  # Check existence via CLI exit status or via filtered output
  set +e
  ctm env show
  ctm config authorization:roles::get -s "role=${user_code}" | grep ${user_code}
  if [ "$?" -eq "0" ]; then
    echo "Role '${user_code}' already exists."
  else
    echo "Creating role '${user_code}'"
    ctm config authorization:role::add ${build_file}
  fi
  set -e
}


function Create_TD_User {
  local user="${1:?usage: Create_TD_User <user> <user_code>}"
  local user_code="${2:?usage: Create_TD_User <user> <user_code>}"
  local template_file=$3
  local build_file=/tmp/user_build_file.json

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
        ' > ${build_file}

    ctm config authorization:user::update "${user}" ${build_file}
  else
    # Create new user via templated JSON
    user="${user}" user_code="${user_code}" \
      envsubst < ${template_file} > ${build_file}

    echo "Adding user '${user}' using ${build_file}"
    ctm config authorization:user::add ${build_file}
  fi
}


function Create_TD_Token {
  local user_code=$1
  local template_file=$2
  local build_file=/tmp/token_build_file.json
  # Ensure required tools exist
  command -v ctm >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }
  command -v jq  >/dev/null 2>&1 || { echo "Error: 'jq' not found."       >&2; return 127; }

  # Build template must exist
  if [[ ! -s ${template_file} ]]; then
    echo "Error: ${template_file} not found or empty." >&2
    return 2
  fi
  user_code=${user_code} envsubst < ${template_file} > ${build_file}
  
  # Create token; catch failures without breaking the whole script
  local token
  if ! token="$(ctm authentication token::create -f ${build_file} 2>/dev/null | jq -r '.tokenValue')"; then
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
  helm upgrade --install "${ctm_user_code}" controlm/saas-controlm-agent --version "9.22.050" \
    --set image.tag="9.22.050-k8s-mft-openjdk" \
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
    --set mft.pvcs[0].name="mft-pvc" \
    --set mft.pvcs[0].mountPath="/mft_mountPath" \
    --set mft.configParametersConfigMapName="mft-config-params" \
    --set ai.additionalPluginsConfigMapName="plugins-list" \
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

  if [[ "INVITE" == "INVITE" ]]; then
    Create_TD_Role       "${ctm_user_code}" "${USER_HOME}/${BASE_DIR}/common/templates/role_saas_attendee.json"
    if [[ "${ctm_user}" != "tst-inst@example.com" ]]; then 
      Create_TD_User       "${ctm_user}" "${ctm_user_code}" "${USER_HOME}/${BASE_DIR}/common/templates/user.json"
    fi
    Create_TD_Token      "${ctm_user_code}" "${USER_HOME}/${BASE_DIR}/common/templates/api_token.json"
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


# Detect sed flavor and set inline flag
sed_inline() {
  # GNU sed supports: sed -i
  if sed --version >/dev/null 2>&1; then
    printf -- '-i'
  else
    # BSD/macOS sed requires -i '' (empty suffix)
    printf -- "-i ''"
  fi
}

# Escape a string to be used as a literal sed regex pattern:
# - Escape regex metacharacters: . ^ $ * + ? ( ) [ ] { } | \
# - Also escape the chosen delimiter (|)
escape_sed_pattern() {
  local s=$1
  s=${s//\\/\\\\}  # backslash -> \\ 
  s=${s//\//\/}    # (not used as delimiter, but keep for safety)
  s=${s//|/\\|}    # escape delimiter
  # Escape regex metas:
  s=${s//./\\.}
  s=${s//^/\\^}
  s=${s//$/\\$}
  s=${s//\*/\\*}
  s=${s//+/\\+}
  s=${s//\?/\\?}
  s=${s//\(/\\(}
  s=${s//\)/\\)}
  s=${s//[/\\[}
  s=${s//]/\\]}
  s=${s//\{ /\\{ } # space to avoid brace expansion in some shells
  s=${s//\{/\\{}
  s=${s//\}/\\}}
  s=${s//|/\\|}
  printf '%s' "$s"
}

# Escape replacement text for sed 's///':
# - Escape '&' (it expands to the matched text otherwise)
# - Escape backslashes
# - Escape delimiter '|'
# - Preserve literal newlines/spaces (bash will pass them through)
escape_sed_replacement() {
  local s=$1
  s=${s//\\/\\\\}  # backslash -> \\
  s=${s//&/\\&}    # ampersand -> \&
  s=${s//|/\\|}    # delimiter -> \|
  printf '%s' "$s"
}


function Repo_Replacements {

  local repo_dir=$1
  local replacements="$2"
  local IFS=' '

  read -r -a tokens <<< "$replacements"
  delimiter="="
  
  for replacement in "${tokens[@]}"; do
    echo "Processing ${replacement}"
    find_str=${replacement%${delimiter}*}
    repl_str=${replacement#*${delimiter}}
    echo "Replacing ${find_str} with ${repl_str} in ${repo_dir}/..."
    find "${repo_dir}/" -type f -exec sed -i "s|${find_str}|$repl_str|g" {} +
    echo "Replacement complete."

  done
  set +f
}

function Repo_Replacements2 {

  local repo_dir=$1
  local arg=$2
  local -a parts
  
  # Choose an uncommon delimiter (Unit Separator)
  local SED_DELIM="|"


  # Split on '|' while preserving newlines (and everything else)
  mapfile -d '|' -t parts < <(printf '%s' "$arg")

  # Get inline flag for sed
  local inline_flag
  inline_flag=$(sed_inline)

  # Iterate over parts
  for i in "${!parts[@]}"; do
    part="${parts[i]}"
    echo "$i ${part}"
    
    # Skip empty segments (e.g., trailing '|')
    [[ -z $part ]] && continue
  
    # Split into key and value at the first '='
    if [[ $part != *'='* ]]; then
      printf 'WARN: segment has no "=" and was skipped: %q\n' "$part" >&2
      continue
    fi
    local key=${part%%=*}
    local value=${part#*=}
  
    
    # Escape for sed
    local pat repl
    #pat=$(escape_sed_pattern "$key")
    pat="$key"
    repl=$(escape_sed_replacement "$value")
    
    # Build one sed script using the uncommon delimiter
    local script="s${SED_DELIM}${pat}${SED_DELIM}${repl}${SED_DELIM}g"
    script=$(printf '%s' "$script" | tr -d '\r')
    
    # Trace a safe one-line preview (doesn't affect sed)
    printf 'sed script (escaped preview): %q\n' "$script" >&2


    # Perform in-place replacement of ALL occurrences
    # Use '|' as s/// delimiter to avoid slash-heavy JSON issues.
    # Note: bash passes literal newlines in $repl just fine.
    # shellcheck disable=SC2086
    #eval sed $inline_flag -e "s|$pat|$repl|g" -- "$file"
    #find "${repo_dir}" -type f -print0 | xargs -0 sed -i -e "s|$pat|$repl|g"

    
    if sed --version >/dev/null 2>&1; then
      # GNU sed
      find "$repo_dir" -type f -exec sed $inline_flag -e "$script" {} +
    else
      # BSD/macOS sed
      find "$repo_dir" -type f -exec sed $inline_flag -e "$script" {} +
    fi


  done
}

function Config_Code_Server {
  local user_home="${1:?usage: Config_Code_Server <user_home> <base_dir> <user>}"
  local base_dir="${2:?usage: Config_Code_Server <user_home> <base_dir> <user>}"
  local user="${3:?usage: Config_Code_Server <user_home> <base_dir> <user>}"

  # Ensure code-server is available (fail fast if missing)
  command -v code-server >/dev/null 2>&1 || { echo "Error: 'code-server' not found on PATH." >&2; return 127; }

  # Start code-server using systemctl
  user=${user} project_dir=${user_home}/${base_dir} \
    envsubst < ${user_home}/${base_dir}/common/templates/code-server.service > /etc/systemd/system/code-server.service
  systemctl enable code-server
  systemctl daemon-reload
  systemctl start code-server
  
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
