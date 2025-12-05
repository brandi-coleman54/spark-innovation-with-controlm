
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


