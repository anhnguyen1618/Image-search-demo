#!/bin/bash
gcloud auth configure-docker
docker build -t eu.gcr.io/gothic-module-289816/indexing:latest . -f ./index/Dockerfile
docker push eu.gcr.io/gothic-module-289816/indexing:latest 

docker build -t eu.gcr.io/gothic-module-289816/serving:latest . -f ./extractors/Dockerfile
docker push eu.gcr.io/gothic-module-289816/serving:latest

docker build -t eu.gcr.io/gothic-module-289816/extract_worker:latest . -f ./extract_worker/Dockerfile
docker push eu.gcr.io/gothic-module-289816/extract_worker:latest

docker build -t eu.gcr.io/gothic-module-289816/rabbitmq_wrapper:latest . -f ./rabbitmq_wrapper/Dockerfile
docker push eu.gcr.io/gothic-module-289816/rabbitmq_wrapper:latest

docker tag rabbitmq:3.8-management eu.gcr.io/gothic-module-289816/rabbitmq:latest
docker push eu.gcr.io/gothic-module-289816/rabbitmq:latest