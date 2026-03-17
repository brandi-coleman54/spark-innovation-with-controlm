#!/bin/bash

SERVER=$1            # ctm server name
AGENT_PREFIX=$2      # this is the prefix for the agentless name
AGENT_COUNT=$3      # number of agentless machines to add
RUNNIN_JOBS=$4
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for ((i=1; i<=AGENT_COUNT; i++)); do


done
