#!/bin/bash

set -euxo pipefail

# Variables
USER="controlm"
GROUP="controlm"
HOME_DIR="/home/$USER"
DEST_DIR="$HOME_DIR/labs"

# CTM Provision Variables
CTM_ENV=${CTM_ENV}
CTM_AAPI_ENDPOINT=${CTM_AAPI_ENDPOINT}
CTM_AAPI_TOKEN=${CTM_AAPI_TOKEN}


# Check if INSTRUQT_USER_EMAIL is set and non-empty
if [[ -z "${INSTRUQT_USER_EMAIL:-}" ]]; then
  echo "INSTRUQT_USER_EMAIL is not set. Using default value."
  CTM_USER="unknown@example.com"
else
  CTM_USER="${INSTRUQT_USER_EMAIL}"
fi

echo "CTM_USER: $CTM_USER"

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

# Generate a random single-digit number (from 0 to 19).
random_digit=$((RANDOM % 20))

# Concatenate the parts to create the final user code.
user_code=$(echo "${first_initial}${last_initials}${random_digit}" | tr '[:upper:]' '[:lower:]')

agent variable set CTM_USER_CODE ${user_code}
agent variable set CTM_USER ${CTM_USER}

agent variable set CTM_AAPI_ENDPOINT ${CTM_AAPI_ENDPOINT}

hostnamectl set-hostname ${_SANDBOX_ID}

cd "$HOME_DIR"

# Set ownership and make all files editable by the user
chown -R "$USER:$GROUP" /home/controlm/spark-innovation-with-controlm

# Activate immediately for current session
export BMC_INST_JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=/home/controlm/venv/bin:$PATH

ctm env add ${CTM_ENV} ${CTM_AAPI_ENDPOINT} ${CTM_AAPI_TOKEN}

function Create_TD_Role {
    user_code=$1

    user_code=${user_code} uc_user_code=${user_code^^} envsubst < /tmp/role_template_file.json > /tmp/role_def_sub.json

    ctm config authorization:roles::get -s "role=${user_code}" | grep ${user_code}
    
    if [ $? -eq 0 ]; then
        echo "Role ${user_code} already exists."
    else
        echo "Creating Role ${user_code}"
        ctm config authorization:role::add /tmp/role_def_sub.json
    fi
}

function Create_TD_User {
    user=$1
    user_code=$2
    
    ctm config authorization:user::get ${user} > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "User ${user} already exists, adding role to existing user instead."
        
    else
        user=${user} user_code=${user_code} envsubst < /tmp/user_template_file.json > /tmp/user_def_sub.json
        echo "Adding user ${user} using /tmp/user_def_sub.json"
        ctm config authorization:user::add /tmp/user_def_sub.json 
    fi
}

function Create_TD_Token {
  
  CTM_AUTH_TOKEN=$(ctm authentication token::create -f /tmp/token_template_file.json | jq -r '.tokenValue') 
   
  if [[ -n "$CTM_AUTH_TOKEN" && "$CTM_AUTH_TOKEN" != "null" ]]; then
        agent variable set CTM_AUTH_TOKEN ${CTM_AUTH_TOKEN}
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
            "AutomationAPIAccess": "Full"
        },
        "Monitoring": {
            "Alert": "Browse"
        },
        "Tools": {
            "SiteStandardPolicies": "Update"
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
    "Calendars": [
        {
            "Privilege": "Update",
            "ControlmServer": "*",
            "Name": "*"
        }
    ],
    "RunasUsers": [
        {
            "ControlmServer": "IN01",
            "RunasUser": "*",
            "Host": "${user_code}*"
        }
    ],
    "SiteStandard": [
        {
            "Privilege": "Update",
            "Name": "*"
        }
    ],
    "Services": [
        {
            "Privilege": "None",
            "Name": "${user_code}*",
            "AllowedActions": {
                "DrillDown": true
            }
        }
    ],
    "AgentManagement": [
        {
            "ControlmServer": "IN01",
            "Agent": "instruqt",
            "Privilege": "Full"
        }
    ],
    "PluginManagement": [
        {
            "ControlmServer": "IN01",
            "Agent": "instruqt",
            "PluginType": "*",
            "Privilege": "Browse"
        }
    ],
    "ConnectionProfileManagement": [
        {
            "ControlmServer": "*",
            "Agent": "*",
            "PluginType": "*",
            "Name": "${user_code}*",
            "Privilege": "Update"
        }
    ]
}
EOF
}


Build_Role_Template ${user_code}
Build_User_Template ${user_code} ${CTM_USER}
Build_Token_Template ${user_code}

Create_TD_Role ${user_code} 
Create_TD_User ${CTM_USER} ${user_code}
Create_TD_Token ${user_code}



TARGET_DIR="/home/controlm/spark-innovation-with-controlm/"

# Function to update JSON key values safely with jq
replace_with_jq() {
    local key="$1"
    local value="$2"
    local file="$3"

    # Use jq to replace any string value matching the placeholder
    jq --arg val "$value" '
        (.. | select(type == "string") | select(. == "'"$key"'")) |= $val
    ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
}


# Replace all instances of 'replace-with-endpoint' with CTM_AAPI_ENDPOINT
echo "Replacing 'replace-with-endpoint' with '${CTM_AAPI_ENDPOINT}' in /home/controlm/spark-innovation-with-controlm/dominos-controlm/scripts..."
find "/home/controlm/spark-innovation-with-controlm/" -type f -exec sed -i "s|replace-with-endpoint|${CTM_AAPI_ENDPOINT}|g" {} +
echo "Replacement complete."
echo "Replacing 'replace-with-email' with '${CTM_USER}' in /home/controlm/spark-innovation-with-controlm/dominos-controlm/scripts..."
find "/home/controlm/spark-innovation-with-controlm/" -type f -exec sed -i "s|replace-with-email|${CTM_USER}|g" {} +
echo "Replacement complete."
echo "Replacing 'replace-with-usercode' with '${user_code}' in /home/controlm/spark-innovation-with-controlm/dominos-controlm/scripts..."
find "/home/controlm/spark-innovation-with-controlm/" -type f -exec sed -i "s|replace-with-usercode|${user_code}|g" {} +
echo "Replacement complete."
echo "Replacing 'replace-with-instruqt-host' with '${user_code}_instruqt_server' in /home/controlm/spark-innovation-with-controlm/dominos-controlm/scripts..."
find "/home/controlm/spark-innovation-with-controlm/" -type f -exec sed -i "s|replace-with-instruqt-host|${user_code}_instruqt_server|g" {} +
echo "Replacement complete."
echo "Replacing 'replace-with-token' with '${CTM_AUTH_TOKEN}' in /home/controlm/spark-innovation-with-controlm/dominos-controlm/scripts..."
find "/home/controlm/spark-innovation-with-controlm/" -type f -exec sed -i "s|replace-with-token|${CTM_AUTH_TOKEN}|g" {} +
echo "Replacement complete."
echo "Replacing 'replace-with-ctm-server' with 'IN01' in /home/controlm/spark-innovation-with-controlm/..."
find "/home/controlm/spark-innovation-with-controlm/" -type f -exec sed -i "s|replace-with-ctm-server|IN01|g" {} +
echo "Replacement complete."
echo "Replacing 'replace-with-ctm-folder' with '${user_code}_Pizza_Order_Workflow_preprod' in /home/controlm/spark-innovation-with-controlm/dominos-controlm/scripts.."
find "/home/controlm/spark-innovation-with-controlm/" -type f -exec sed -i "s|replace-with-ctm-folder|${user_code}_Pizza_Order_Workflow|g" {} +
echo "Replacement complete."

# Set ownership and make all files editable by the user
chown -R "$USER:$GROUP" /home/controlm/spark-innovation-with-controlm
