#!/bin/bash
kubectl delete svc --all
kubectl delete sts --all
kubectl delete deployments --all
kubectl delete pod --all
kubectl delete pvc --all
kubectl delete pv --all
