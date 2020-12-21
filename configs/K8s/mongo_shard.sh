#!/bin/bash
SHARD_COUNT=2
shards=0
time_count=0
max_count=50

while [[ $shards -lt $SHARD_COUNT ]]
do
  echo "================== Creating shard-$shards =================="
  echo "Setting shard-$shards replicate..."
  
  while [[ $(oc get pods -l appdb=mongodb-shard$shards -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True True True" ]]; do
    if [[ $time_count -eq $max_count ]]; then
      echo "Pods are unreponsive after 2 mins. Exiting..."
      exit 1
    fi

    echo "Waiting for pods..."
    sleep 5
    time_count=$(($time_count+1))
  done
  time_count=0

  # Wait for pods connections to set up
  sleep 20

  oc exec mongodb-shard$shards-0 -- mongo --eval "rs.initiate({_id: \"shard$shards\", members: [{_id : 0, host : \"mongodb-shard$shards-0.mongodb-shard$shards.mongo.svc.cluster.local:27017\"}, {_id : 1, host : \"mongodb-shard$shards-1.mongodb-shard$shards.mongo.svc.cluster.local:27017\"}, {_id : 2, host : \"mongodb-shard$shards-2.mongodb-shard$shards.mongo.svc.cluster.local:27017\"}]});"

  # {_id: 0, host: \"mongodb-shard$shards-0.mongodb-shard$shards.mongo.svc.cluster.local:27017\"},

  oc exec $(oc get pods -l name=mongos -o=jsonpath='{.items[0].metadata.name}')  -- mongo --eval "sh.addShard(\"shard$shards/mongodb-shard$shards-0.mongodb-shard$shards.mongo.svc.cluster.local:27017\");"
  echo "================== Shard-$shards created! =================="
  shards=$(($shards+1))
done
oc exec $(oc get pods -l name=mongos -o=jsonpath='{.items[0].metadata.name}')  -- mongo --eval "sh.enableSharding('features');"
oc exec $(oc get pods -l name=mongos -o=jsonpath='{.items[0].metadata.name}')  -- mongo --eval "sh.shardCollection('features.vgg19', {_id: \"hashed\"}); sh.shardCollection('features.inception', {_id: \"hashed\"}); sh.shardCollection('features.mobilenet', {_id: \"hashed\"}); sh.shardCollection('features.vgg16', {_id: \"hashed\"}); sh.shardCollection('features.xception', {_id: \"hashed\"}); sh.shardCollection('features.resnet', {_id: \"hashed\"}); sh.shardCollection('features.custom', {_id: \"hashed\"})"
# sh.shardCollection('features.{db_name}', {_id: \"hashed\"});
echo "================== Succesfully config shard key! =================="