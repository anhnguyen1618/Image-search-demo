for svc_name in $(oc get svc -l service='extract_worker' -o=jsonpath='{.items[*].metadata.name}')
do
    oc get pods -l app=$svc_name -o=jsonpath='{.items[*].metadata.name}'
done