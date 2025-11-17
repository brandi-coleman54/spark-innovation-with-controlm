#!/bin/bash

URL=$1
TARG_DIR=$2
CTM_ENV=$3
AAPI_ENDPOINT=$4
AAPI_TOKEN=$5

function Install_AAPI {

  ctm_cli_url=$1
  install_dir=$2

  cd ${install_dir}
  curl -O ${ctm_cli_url}
  
  # Extract the filename from url
  filename=$(basename ${ctm_cli_url})
  echo "ctm_cli_url filename is ${filename}"
  
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

Install_AAPI ${URL} ${TARG_DIR}
Add_AAPI_Env ${CTM_ENV} ${AAPI_ENDPOINT} ${AAPI_TOKEN}
