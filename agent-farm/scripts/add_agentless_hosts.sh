#!/bin/bash

PREFIX=1
SERVER=$2
OPER=$3
NAME=$4
COUNT=${5:-}

# Build assoc agents array string

if [[ "$OPER" == "single" ]]; then
  ctm config server:agentlesshost::add <server> <agentlesshost>
