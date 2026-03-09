#!/bin/bash

VENV_DIR=$1
PREFIX=$2
SERVER=$3
COUNT=$4
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source ${VENV_DIR}/venv/bin/activate

for ((i=1; i<=${COUNT}; i++)); do
  agent=${PREFIX}${i}
  tries=1
  until ctm config server:agents::get ${SERVER} -s "agent=${agent}" | jq 'has("operatingSystem")'; do
    echo "Try for OS ${tries}"
    if [ "${tries}" -ge "20" ]; then
      echo "breaking"
      break
    fi
    sleep 30
    ((tries++))
  done
done
