import subprocess

class GenConfig():
    def __init__(self, out_dir="./staging"):
        self.template_dir = "./templates"
        self.out_dir= out_dir 
    def get_services(self):
        services=["extract-worker", "indexing", "serving"]
        result = []
        for service in services:
            sub_service_names = subprocess.getoutput(f"oc get svc -l service='{service}'" + " -o=jsonpath='{.items[*].metadata.name}'").split(" ")
            for sub_service in sub_service_names:
                pod_names = subprocess.getoutput(f"oc get pods -l app={sub_service}" + " -o=jsonpath='{.items[*].metadata.name}'").split(" ")
                result.append((sub_service, pod_names))
        return result 

    def gen_content(self):
        content = ""
        results = self.get_services()
        for service_name, pod_names in results:
            content += f"    - job_name: {service_name}\n      metrics_path: /metrics\n      static_configs:\n        - targets:\n"

            for pod_name in pod_names:
                content += f"            - '{pod_name}.{service_name}.mongo.svc.cluster.local:5000'\n"
            content += "\n"
        return content 

        
    def gen(self):
        template_file = open(f"{self.template_dir}/prometheus-config.yml")
        content = self.gen_content()
        content = template_file.read().replace("{jobs}", content)
        file_path = f"{self.out_dir}/prometheus-config.yml"
        file = open(file_path, "w") 
        file.write(content) 
        file.close() 
            

if __name__ == '__main__':
    gen = GenConfig("./K8s")
    gen.gen()
    subprocess.run("oc apply -f ./K8s/prometheus-config.yml && oc exec -it $(oc get pod -l app=prometheus -o=jsonpath='{.items[*].metadata.name}') -- sh -c 'kill -HUP 1'", shell=True)

