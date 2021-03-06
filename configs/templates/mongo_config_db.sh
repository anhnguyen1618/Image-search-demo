#!/bin/bash
time_count=0
max_count=50
echo "============== Creating config pods (~1 min) =============="
while [[ $(oc get pods -l name="configdb" -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "{condition_result}" ]]
do
    if [[ $time_count -eq $max_count ]]; then
      echo "Pods are unreponsive after 2 mins. Exiting..."
      exit 1
    fi
    echo "-------------waiting for config pod------------"
    sleep 5
    time_count=$(($time_count+1))
done

#sleep 20

echo "==========Pods are created!============="

oc exec configdb-0 -- mongo --eval "rs.initiate(
  {
    _id: \"cfgrs\",
    configsvr: true,
    members: [
        {data_replicates}
    ]
  }
)"

echo "==========Set up configuration done!============="