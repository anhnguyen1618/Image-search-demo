#!/bin/bash
# docker tag 1aaf554283a7 zozonguyen1/serving:v1
# docker push zozonguyen1/serving
oc apply -f ../K8s/rabbitmq.yml
oc apply -f ../K8s/rabbitmq_wrapper.yml
oc apply -f ../K8s/mongo.yml
oc apply -f ../K8s/extract_worker.yml
oc apply -f ../K8s/indexing.yml

oc apply -f ../K8s/serving.yml
oc expose svc serving
echo "Serving service url: $(oc get route serving -o=jsonpath='{.spec.host}')"
oc expose svc rabbitmq-wrapper
echo "Rabbitmq wrapper service url: $(oc get route rabbitmq-wrapper -o=jsonpath='{.spec.host}')"
oc expose svc indexing
echo "Rabbitmq wrapper service url: $(oc get route indexing -o=jsonpath='{.spec.host}')"
