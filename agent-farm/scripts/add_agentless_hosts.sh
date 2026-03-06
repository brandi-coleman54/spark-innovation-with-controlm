#!/bin/bash

PREFIX=1
SERVER=$2
OPER=$3
NAME=$4
COUNT=${5:-}
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Build assoc agents array string
assoc_ct=$(ctm config server:agents::get ${SERVER} -s "agent=${PREFIX}*" | jq '.agents | length'
assoc_str=""
for ((i=0; i<assoc_ct; i++)); do
  assoc_str+="\"${PREFIX}${i}\","
done
assoc_str="${assoc_str%,}"

assoc_agents=${assoc_str} envsubst < ${SCRIPT_DIR}/../templates/agentless_config.json > agentless_config.json


if [[ "${OPER}" == "single" ]]; then
  ctm config server:agentlesshost::add ${SERVER} ${NAME} -f agentless_config.json
fi

if [[ "${OPER}" == "count" ]]; then
  for ((i=1; i<=${COUNT}; i++)); do
    ctm config server:agentlesshost::add ${SERVER} ${NAME}${i} -f agentless_config.json
  done
fi
