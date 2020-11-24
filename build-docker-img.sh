#!/bin/bash
# docker build -t zozonguyen/indexing:latest . -f ./index/Dockerfile
# docker push zozonguyen/indexing

# docker build -t zozonguyen/serving:latest . -f ./extractors/Dockerfile
# docker push zozonguyen/serving

# docker build -t zozonguyen/extract_worker:latest . -f ./extract_worker/Dockerfile
# docker push zozonguyen/extract_worker

docker build -t zozonguyen/rabbitmq_wrapper:latest . -f ./rabbitmq_wrapper/Dockerfile
docker push zozonguyen/rabbitmq_wrapper