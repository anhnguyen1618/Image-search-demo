#!/bin/bash
kubectl apply -f "../k8s-config/config-deployment.yaml"

time_count=0
echo "============== Creating config pods =============="
while [[ $(kubectl get pods -l name="configdb" -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True True True" ]]; do      if [[ $time_count -eq 40 ]]; then
      echo "Pods are unreponsive after 2 mins. Exiting..."
      exit 1
  fi
  echo "-------------waiting for config pod------------"
  sleep 5
  time_count=$(($time_count+1))
done

sleep 20


kubectl exec configdb-0 -- mongo --eval "rs.initiate(
  {
    _id: \"cfgrs\",
    configsvr: true,
    members: [
      { _id : 0, host : \"configdb-0.configdb.default.svc.cluster.local:27017\" },
      { _id : 1, host : \"configdb-1.configdb.default.svc.cluster.local:27017\" },
      { _id : 2, host : \"configdb-2.configdb.default.svc.cluster.local:27017\" }
    ]
  }
)"

echo "==========Set up configuration done!============="