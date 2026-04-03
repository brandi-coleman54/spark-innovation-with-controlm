#!/bin/bash

local CTM_USER_CODE=$1
local USER_HOME=$2
local BASE_DIR=$3

# Control-M Agents install using Helm
helm repo add controlm https://controlm-charts.s3.us-west-2.amazonaws.com/
helm repo update
helm upgrade --install "zzy1" controlm/controlm-agent \
  --values /root/labs/event-driven-workloads/templates/k8s_ag_values.yaml \
  --set server.name="instruqt" \
  --set server.ip="10.32.0.142" \
  --set api.endpoint="https://control-m:8443/automation-api" \
  --set api.token="b25QcmVtOmQ5ZTU1NTAxLWUwMGMtNGEzZS04YzBhLTkzZjFhYTc2YWJiMA==" \
  --set agent.replicas=1 \
  --set agent.tag=sparkit \
  --set server.hostgroup="zzy1-eks-hg" \
  --set-json 'pod.nodeSelector={"kubernetes.io/os":"linux"}' \
  --set-json 'pod.annotations={"cluster-autoscaler.kubernetes.io/safe-to-evict":"false"}' \
  --namespace "zzy1" --create-namespace

kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"

kubectl create namespace messaging
kubectl apply -f ${USER_HOME}/${BASE_DIR}/event-driven-workloads/templates/rabbitmq-cluster.yaml
