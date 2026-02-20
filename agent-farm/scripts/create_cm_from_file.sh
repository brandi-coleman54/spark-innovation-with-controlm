#!/bin/bash

NAMESPACE=$1
CM_NAME=$2
FILE=$3

ROOT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $ROOT_DIR
kubectl delete configmap ${CM_NAME} -n $NAMESPACE
kubectl create configmap ${CM_NAME} --from-file=${FILE} -n $NAMESPACE
