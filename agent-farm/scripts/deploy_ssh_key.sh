#!/bin/bash

VENV_DIR=$1
SERVER=$2
KEY_NAME=$3
KEY_PASS=$4

mkdir -p ~/.ssh
chmod 700 ~/.ssh

source ${VENV_DIR}/venv/bin/activate
key=$(ctm config server:sshkey::get ${SERVER} ${KEY_NAME} ${KEY_PASS} | jq -r '.key')

echo "${key}" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
