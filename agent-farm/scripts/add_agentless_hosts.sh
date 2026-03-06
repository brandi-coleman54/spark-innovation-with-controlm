#!/bin/bash

PREFIX=1
SERVER=$2
OPER=$3
NAME=$4
COUNT=${5:-}

# Build assoc agents array string
assoc_ct=$(ctm config server:agents::get ${SERVER} -s "agent=${PREFIX}*" | jq '.agents | length'
assoc_str=""
for ((i=0; i<assoc_ct; i++)); do
  assoc_str+="\"${PREFIX}${i}\","
done
assoc_str="${assoc_str%,}"



if [[ "$OPER" == "single" ]]; then
  ctm config server:agentlesshost::add <server> <agentlesshost>
