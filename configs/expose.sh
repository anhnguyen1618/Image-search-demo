for svc_name in $(oc get svc -l type='public' -o=jsonpath='{.items[*].metadata.name}')
do
    oc expose svc $svc_name
    echo "Serving service url: $(oc get route $svc_name -o=jsonpath='{.spec.host}')"
done
