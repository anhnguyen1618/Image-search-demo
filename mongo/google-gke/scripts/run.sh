#!/bin/bash
./create_config_svc.sh

./create_router.sh

./create_shard.sh

# mongo 192.168.99.100:31677 /minikube service mongos --url
