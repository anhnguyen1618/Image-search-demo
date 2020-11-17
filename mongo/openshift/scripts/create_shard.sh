#!/bin/bash
SHARD_COUNT=2
shards=0
time_count=0

while [[ $shards -lt $SHARD_COUNT ]]
do
  echo "================== Creating shard-$shards (~30 seconds)=================="
  # Generating template for shard 0, 1...
  sed "s/shardX/shard$shards/g" "../k8s-config/shard-deployment.yaml" > "../k8s-config/shard$shards-deployment.yaml"
  oc apply -f "../k8s-config/shard$shards-deployment.yaml"

  echo "Setting shard-$shards replicate..."
  
  while [[ $(oc get pods -l appdb=mongodb-shard$shards -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True True True" ]]; do
    if [[ $time_count -eq 24 ]]; then
      echo "Pods are unreponsive after 2 mins. Exiting..."
      exit 1
    fi

    echo "Waiting for pods..."
    sleep 5
    time_count=$(($time_count+1))
  done
  time_count=0

  # Wait for pods connections to set up
  # sleep 20
  echo "Start with set replicate"
  oc exec mongodb-shard$shards-0 -- mongo --eval "rs.initiate({_id: \"shard$shards\", members: [ {_id: 0, host: \"mongodb-shard$shards-0.mongodb-shard$shards.mongo.svc.cluster.local:27017\"}, {_id: 1, host: \"mongodb-shard$shards-1.mongodb-shard$shards.mongo.svc.cluster.local:27017\"}, {_id: 2, host: \"mongodb-shard$shards-2.mongodb-shard$shards.mongo.svc.cluster.local:27017\"} ]});"

  echo "Done with set replicate"

  oc exec $(oc get pods -l name=mongos -o=jsonpath='{.items[0].metadata.name}')  -- mongo --eval "sh.addShard(\"shard$shards/mongodb-shard$shards-0.mongodb-shard$shards.mongo.svc.cluster.local:27017\");"
  echo "================== Shard-$shards created! =================="
  shards=$(($shards+1))
done

oc exec $(oc get pods -l name=mongos -o=jsonpath='{.items[0].metadata.name}')  -- mongo --eval "sh.enableSharding('client_1'); sh.shardCollection('client_1.records', {_id: 'hashed'}); sh.enableSharding('client_2'); sh.shardCollection('client_2.records', {_id: 'hashed'});"
echo "================== Succesfully config shard key! =================="