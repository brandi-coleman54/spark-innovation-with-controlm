#!/bin/bash

SERVER=$1            # ctm server name
AGENT_PREFIX=$2      # this is the prefix for the agentless name
AGENT_COUNT=$3      # number of agentless machines to add
RUNNING_JOBS=$4
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for ((i=1; i<=AGENT_COUNT; i++)); do
  policy_name=AGENTLESS${i}_THROTTLE \
  agent_name=${AGENT_PREFIX}${i} \
  running_jobs=${RUNNING_JOBS} \
  server=${SERVER} \
    envsubst < ${SCRIPT_DIR}/../templates/wp_throttle_agentless.json > /tmp/wp_${i}.json
  ctm run workloadpolicies::add /tmp/wp_${i}.json
  ctm run workloadpolicies::activate AGENTLESS${i}_THROTTLE
done
