for pod_name in $(oc get pods -l service='indexing' -o=jsonpath='{.items[*].metadata.name}')
do
    echo "Update index for $pod_name"
    oc exec -it $pod_name -- bash -c "curl 127.0.0.1:5000/reindex" 
    echo ""
done
