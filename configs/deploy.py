import os, json, sys, stat, random, string
import subprocess

stage_dir = "./staging"
main_dir = "./K8s"

class Common_generator:
    def __init__(self, data, model_meta = {}):
        self.data = data
        self.template_dir = "./templates"
        self.out_dir = stage_dir 
        self.model_meta = model_meta

    def gen(self, extra_data = None):
        print(f"Service {self.data['name']} generator is missing")

class Extract_worker(Common_generator):
    def gen_from_template(self, model_name, num_pods, deduplicate_model, deduplicate_threshold, model_url = ""):
        template_file = open(f"{self.template_dir}/extract_worker.yml")
        template_content = template_file.read()

        content = (
            template_content
            .replace("{model}", model_name)
            .replace("{model_url}", model_url)
            .replace("{num_pods}", str(num_pods))
            .replace("{deduplicate_model}", str(deduplicate_model))
            .replace("{deduplicate_threshold}", str(deduplicate_threshold))
            )
        file = open(f"{self.out_dir}/extract_worker-{model_name}.yml", "w") 
        file.write(content) 
        file.close()  
    
    def extract_deduplicate_info(self):
        models = self.data["models"]
        print(models)
        if len(models) == 1:
            return {"model": models[0]["name"], "threshold": models[0].get("deduplicate_threshold", 0)}

        for _, model in self.model_meta.items():
            if model.get("deduplicate", False):
                return {"model": model["name"], "threshold": model.get("deduplicate_threshold", 0)}

        raise Exception("It is required to specify deduplicate model")


    def gen(self, extra_data = None):
        deduplicate_info = self.extract_deduplicate_info()
        for model in self.data["models"]:
            model_name = model["name"]
            model_url = self.model_meta.get(model_name, {}).get("model_url", "") 
            self.gen_from_template(model_name, model["pods"], deduplicate_info["model"], deduplicate_info["threshold"], model_url)

class Indexing(Common_generator):
    def gen_from_template(self, model_name, num_indexes, num_pods, index_algorithm = "brute", model_url = ""):
        template_file = open(f"{self.template_dir}/indexing.yml")
        template_content = template_file.read()
        for index_num in range(1, num_indexes + 1):
            content = (
                template_content
                .replace("{model}", model_name)
                .replace("{model_url}", model_url)
                .replace("{index_algorithm}", index_algorithm)
                .replace("{num_indexes}", str(num_indexes))
                .replace("{index_num}", str(index_num))
                .replace("{num_pods}", str(num_pods)))
            file = open(f"{self.out_dir}/indexing-{model_name}-{index_num}.yml", "w") 
            file.write(content) 
            file.close() 
        
    def gen(self, extra_data = None):
        for model in self.data["models"]:
            model_name = model["name"]
            model_url = self.model_meta.get(model_name, {}).get("model_url", "") 
            self.gen_from_template(model_name, model["num_indexes"], model["pods"], model.get("index_algorithm", "brute"), model_url)
        pass

class Serving(Common_generator):
    def __init__(self, data, model_meta):
        super().__init__(data, model_meta)
        self.models_data = data["models"]
    
    def get_indexes_info(self, index_data):
        result = {}
        if not index_data:
            return result

        for svc in index_data["services"]:
            if svc["name"] == "indexing":
                indexing_models = svc["models"]
                for model in indexing_models:
                    result[model["name"]] = model["num_indexes"]
        return result 
    
    def gen_from_template(self, model_name, num_pods, num_indexes, model_url = ""):
        template_file = open(f"{self.template_dir}/serving.yml")
        content = template_file.read().replace("{model}", model_name).replace("{model_url}", model_url).replace("{num_pods}", str(num_pods)).replace("{num_indexes}", str(num_indexes))
                
        file = open(f"{self.out_dir}/serving-{model_name}.yml", "w") 
        file.write(content) 
        file.close() 


    def gen(self, extra_data = None):
        indexes = self.get_indexes_info(extra_data) 
        for model in self.models_data:
            model_name = model["name"]
            num_indexes = indexes.get(model_name, 0)
            num_pods = model["pods"]
            model_url = self.model_meta.get(model_name, {}).get("model_url", "") 
            if num_indexes == 0:
                print(f"ERROR: Could not found index service for model {model_name}")
                continue
            
            self.gen_from_template(model_name, num_pods, num_indexes, model_url)

class Rabbitmq_wrapper(Common_generator):
    def gen(self, extra_data = None):
        template_file = open(f"{self.template_dir}/rabbitmq_wrapper.yml")
        content = template_file.read().replace("{num_pods}", str(self.data["pods"]))
        file = open(f"{self.out_dir}/rabbitmq_wrapper.yml", "w") 
        file.write(content) 
        file.close()

class Rabbitmq(Common_generator):
    def gen(self, extra_data = None):
        template_file = open(f"{self.template_dir}/rabbitmq.yml")
        content = template_file.read().replace("{num_pods}", str(self.data["pods"]))
        file = open(f"{self.out_dir}/rabbitmq.yml", "w") 
        file.write(content) 
        file.close()

class Nginx(Common_generator):
    def gen_config(self):
        server_content = ""
        for model in self.data["serving_weights"]:
            server_content += f"server serving-{model['name']}:5000 weight={model['weight']};\n    "
        return server_content

        # template_file = open(f"{self.template_dir}/nginx.conf")
        # content = template_file.read().replace("{servers}", server_content)
        # file = open(f"{self.out_dir}/nginx.conf", "w") 
        # file.write(content) 
        # file.close()
    
    # def build_docker_img(self):
    #     execute(f"cp {self.template_dir}/Dockerfile-nginx staging")
    #     os.chdir("staging")
    #     execute("docker build -t eu.gcr.io/gothic-module-289816/nginx:latest . -f Dockerfile-nginx")
    #     execute("docker push eu.gcr.io/gothic-module-289816/nginx:latest")
    #     execute("rm Dockerfile-nginx")
    #     os.chdir("..")

    def gen(self, extra_data = None):
        template_file = open(f"{self.template_dir}/nginx.yml")
        server_content = self.gen_config()
        content = template_file.read().replace("{servers}", server_content).replace("{num_pods}", str(self.data["pods"]))
        file = open(f"{self.out_dir}/nginx.yml", "w") 
        file.write(content) 
        file.close()

class Prometheus(Common_generator):
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

        
    def gen_config(self):
        template_file = open(f"{self.template_dir}/prometheus.yml")
        content = self.gen_content()
        content = template_file.read().replace("{jobs}", content).replace("{num_pods}", str(self.data["pods"]))
        file_path = f"{self.out_dir}/prometheus.yml"
        file = open(file_path, "w") 
        file.write(content) 
        file.close() 
    
    # def build_docker_img(self):
    #     execute(f"cp {self.template_dir}/Dockerfile-prometheus staging")
    #     os.chdir("staging")
    #     execute("docker build -t eu.gcr.io/gothic-module-289816/prometheus:latest . -f Dockerfile-prometheus")
    #     execute("docker push eu.gcr.io/gothic-module-289816/prometheus:latest")
    #     execute("rm Dockerfile-prometheus")
    #     execute("rm prometheus_config.yml")
    #     execute("rm alert.yml")
    #     os.chdir("..")
    
    # def gen_yml(self):
    #     template_file = open(f"{self.template_dir}/prometheus.yml")
    #     content = template_file.read().replace("{num_pods}", str(self.data["pods"]).replace("{num_random}", random.choice(string.ascii_letters)))
    #     file = open(f"{self.out_dir}/prometheus.yml", "w") 
    #     file.write(content) 
    #     file.close()

    def gen(self, extra_data = None):
        self.gen_config()
        # self.build_docker_img()
        # self.gen_yml()

class Mongo(Common_generator):
    class Config_db(Common_generator):
        def gen_yml(self):
            template_file = open(f"{self.template_dir}/mongo_config_db.yml")
            content = template_file.read().replace("{num_pods}", str(self.data["pods"]))
            file = open(f"{self.out_dir}/mongo_config_db.yml", "w") 
            file.write(content) 
            file.close()
        
        def gen_script(self):
            template_file = open(f"{self.template_dir}/mongo_config_db.sh")
            num_pods = self.data["pods"]
            condition_result = " ".join(["True" for i in range(num_pods)])
            content = (
                template_file.read()
                    .replace("{condition_result}", condition_result)
                    .replace("{data_replicates}", self.gen_members(num_pods))
            )
            file_path = f"{self.out_dir}/mongo_config_db.sh"
            file = open(file_path, "w") 
            file.write(content) 
            file.close()
            os.chmod(file_path, 0o775)
        
        def gen_members(self, num_pods):
            def get_url(index):
                return f"\\\"configdb-{index}.configdb.mongo.svc.cluster.local:27017\\\""
            return ", ".join(["{" + f"_id : {index}, host : {get_url(index)}" + "}" for index in range(num_pods)])

        def gen(self, extra_data = None):
            self.gen_yml()
            self.gen_script()

    class Router(Common_generator):
        def gen_config_urls_string(self, services):
            for service in services:
                if service["name"] == "config_db":
                    num_config_dbs = service["pods"]
                    return ", ".join([f"configdb-{i}.configdb.mongo.svc.cluster.local:27017" for i in range(num_config_dbs)])
            return "" 

        def gen(self, services = None):
            template_file = open(f"{self.template_dir}/mongo_router.yml")
            config_urls_string = self.gen_config_urls_string(services)
            content = template_file.read().replace("{num_pods}", str(self.data["pods"])).replace("{config_urls}", config_urls_string)
            file = open(f"{self.out_dir}/mongo_router.yml", "w") 
            file.write(content) 
            file.close()

    class Shard(Common_generator):
        def gen_yml(self):
            template_file = open(f"{self.template_dir}/mongo_shard.yml")
            template_content = template_file.read()
            num_pods_per_shard = self.data["pods"]
            num_shards = self.data["shards"]
            for index in range(num_shards):
                content = template_content.replace("{index}", str(index)).replace("{num_pods}", str(self.data["pods"]))
                file = open(f"{self.out_dir}/mongo_shard_{index}.yml", "w") 
                file.write(content) 

        def gen_members(self, num_pods):
            def get_url(index):
                return f"\\\"mongodb-shard$shards-{index}.mongodb-shard$shards.mongo.svc.cluster.local:27017\\\""

            return ", ".join(["{" + f"_id : {index}, host : {get_url(index)}" + "}" for index in range(num_pods)])
        
        def gen_shard_cmds_string(self):
            model_names = {
                'vgg16',
                'vgg19',
                'mobilenet',
                'inception',
                'resnet',
                'xception'
            }
            for model in self.model_meta:
                model_names.add(model)

            return "; ".join([f"sh.shardCollection('features.{model_name}', " + "{_id: \\\"hashed\\\"})" for model_name in model_names])

        def gen_script(self):
            template_file = open(f"{self.template_dir}/mongo_shard.sh")
            num_pods = self.data["pods"]
            num_shards = self.data["shards"]
            condition_result = " ".join(["True" for i in range(num_pods)])

            content = (
                template_file.read()
                    .replace("{num_shards}", str(num_shards))
                    .replace("{condition_result}", condition_result)
                    .replace("{shard_db_cmds}", self.gen_shard_cmds_string())
                    .replace("{data_replicates}", self.gen_members(num_pods))
            )
            file_path = f"{self.out_dir}/mongo_shard.sh"
            file = open(file_path, "w") 
            file.write(content) 
            file.close()
            os.chmod(file_path, 0o775)

        def gen(self, extra_data = None):
            self.gen_yml()
            self.gen_script()

    def __init__(self, data, model_meta = {}):
        super().__init__(data, model_meta)
        self.sub_services = data["services"]
        self.generator_mappings = {
            "config_db": self.Config_db,
            "router": self.Router,
            "shard": self.Shard
        }

    def gen(self, extra_data = None):
        for sub_service in self.sub_services:
            generator = self.generator_mappings.get(sub_service["name"], Common_generator)(sub_service, self.model_meta)
            generator.gen(self.sub_services)

class Generator:
    def __init__(self, path):
        file = open(path)
        self.data = json.load(file)
        self.generator_mappings = {
            "extract_worker": Extract_worker,
            "indexing": Indexing,
            "serving": Serving,
            "rabbitmq_wrapper": Rabbitmq_wrapper,
            "rabbitmq": Rabbitmq,
            "mongo": Mongo,
            "nginx": Nginx,
            "prometheus": Prometheus
        }
        self.model_meta = self.gen_model_meta(self.data.get("models", []))
    
    def gen_model_meta(self, models):
        result = {}
        for model in models:
            name = model["name"]
            result[name] = model 

        return result

    def gen_service(self):
        services = self.data.get("services", [])
        for service in services:
            generator = self.get_generator(service)
            generator.gen(self.data)
    
    def get_generator(self, data):
        return self.generator_mappings.get(data["name"], Common_generator)(data, self.model_meta)

def execute(cmd):
    commands = cmd.split("&&")
    for cmd in commands:
        cmd = cmd.strip()
        subprocess.run(cmd.split(" "))


def clean_and_apply():
    stage_files = set(os.listdir(stage_dir))
    for cur_file in os.listdir(main_dir):
        if cur_file not in stage_files:
            execute(f"oc delete -f {main_dir}/{cur_file}")

    # os.chdir("..")
    # execute("cp templates/volume-claim.yml staging")
    # execute("./build-docker-img.sh")
    # os.chdir("configs")
    execute(f"rm -r {main_dir} && mv {stage_dir} {main_dir} && mkdir {stage_dir}  && oc apply -f {main_dir}")
    execute("sh expose.sh")
    os.chdir(main_dir)
    execute("bash mongo_config_db.sh")
    execute("bash mongo_shard.sh")

if __name__ == '__main__':
    if not os.path.exists(stage_dir):
        os.mkdir(stage_dir)
    
    if not os.path.exists(main_dir):
        os.mkdir(main_dir)

    generator = Generator("config.json")
    generator.gen_service()
    clean_and_apply()
