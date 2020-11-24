#!/bin/bash
docker build -t zozonguyen1/indexing:latest . -f ./index/Dockerfile
docker push zozonguyen1/indexing

docker build -t zozonguyen1/serving:latest . -f ./extractors/Dockerfile
docker push zozonguyen1/serving

docker build -t zozonguyen1/extract_worker:latest . -f ./extract_worker/Dockerfile
docker push zozonguyen1/extract_worker

docker build -t zozonguyen1/rabbitmq_wrapper:latest . -f ./rabbitmq_wrapper/Dockerfile
docker push zozonguyen1/rabbitmq_wrapper