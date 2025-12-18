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


function Set_Hostname {
  local new_hostname="${1:?usage: Set_Hostname <new_hostname>}"
  command -v hostnamectl >/dev/null 2>&1 || { echo "Error: 'hostnamectl' not found." >&2; return 127; }

  if ! hostnamectl set-hostname "${new_hostname}"; then
    echo "Error: failed to set hostname to ${new_hostname}." >&2
    return 1
  fi
}


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
    python "${filename}"
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

function Configure_CTM_User {
  local ctm_user_code="${1:?usage: Configure_CTM_User <ctm_user_code> <ctm_user> <ctm_tst_role> <ctm_tst_token>}"
  local ctm_uc_user_code="${ctm_user_code^^}"
  local ctm_user="${2:?usage: Configure_CTM_User <ctm_user_code> <ctm_user> <ctm_tst_role> <ctm_tst_token>}"
  local ctm_tst_role="${3:-}"   # only used in TEST mode
  local ctm_tst_token="${4:-}" # only used in TEST mode
  

  # Tool checks
  command -v ctm       >/dev/null 2>&1 || { echo "Error: 'ctm' CLI not found." >&2; return 127; }

  if [[ "${MODE:-TEST}" == "INVITE" ]]; then
    Create_TD_Role       "${ctm_user_code}" "${USER_HOME}/${BASE_DIR}/common/templates/role_saas_attendee.json"
    Create_TD_User       "${ctm_user}" "${ctm_user_code}" "${USER_HOME}/${BASE_DIR}/common/templates/user.json"
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
