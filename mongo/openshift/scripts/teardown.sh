#!/bin/bash
oc delete svc --all
oc delete sts --all
oc delete deployments --all
oc delete pod --all
oc delete pvc --all
oc delete pv --all
