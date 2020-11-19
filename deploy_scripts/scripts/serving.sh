#!/bin/bash
# docker tag 1aaf554283a7 zozonguyen/serving:v1
# docker push zozonguyen/serving

oc appply -f ../K8s/serving.yml
oc expose svc serving && echo "Serving service url: $(oc get route serving -o=jsonpath='{.spec.host}')"