#!/bin/bash

VENV_DIR=$1
SERVER=$2            # ctm server name
AGENT_PREFIX=$3      # this is the prefix for the agentless name
AGENT_COUNT=$4      # number of agentless machines to add
RUNNING_JOBS=$5
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source ${VENV_DIR}/venv/bin/activate

for ((i=1; i<=AGENT_COUNT; i++)); do
  policy_name=AGENTLESS${i}_THROTTLE \
  agentless_host=${AGENT_PREFIX}${i} \
  running_jobs=${RUNNING_JOBS} \
  server=${SERVER} \
    envsubst < ${SCRIPT_DIR}/../templates/wp_throttle_agentless.json > /tmp/wp_${i}.json
  ctm run workloadpolicies::add /tmp/wp_${i}.json
  ctm run workloadpolicy::activate AGENTLESS${i}_THROTTLE
done
