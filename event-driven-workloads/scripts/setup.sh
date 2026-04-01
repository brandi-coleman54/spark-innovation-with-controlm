#!/bin/bash

local USER_HOME=$1
local BASE_DIR=$2

kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"

kubectl create namespace messaging
kubectl apply -f ${USER_HOME}/${BASE_DIR}/event-driven-workloads/templates/rabbitmq-cluster.yaml
