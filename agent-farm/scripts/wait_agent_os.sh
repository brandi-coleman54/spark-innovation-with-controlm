#!/bin/bash

PREFIX=$1
SERVER=$2
COUNT=$3
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for ((i=1; i<=${COUNT}; i++)); do
  agent=${PREFIX}${i}
  os=$(ctm config server:agents::get ${SERVER} -s "agent=${agent}" | jq -r '.agents[0].operatingSystem')
  tries=1
  until [[ "${os} != "" ]]; do
    echo "Try for OS ${tries}"
    if [ "${tries}" -ge 20 ]; then
      echo "breaking"
      break
    fi
    sleep 30
    ((tries++))
  done
done
