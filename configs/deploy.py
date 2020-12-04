import os, json
import subprocess

stage_dir = "./staging"
main_dir = "./K8s"

class Common_generator:
    def __init__(self, data):
        self.data = data
        self.template_dir = "./templates"
        self.out_dir = stage_dir 

    def gen(self, extra_data = None):
        print(f"Service {self.data['name']} generator is missing")

class Extract_worker(Common_generator):
    def gen_from_template(self, model_name, num_pods, model_url = ""):
        template_file = open(f"{self.template_dir}/extract_worker.yml")
        template_content = template_file.read()
        content = (
            template_content
            .replace("{model}", model_name)
            .replace("{model_url}", model_url)
            .replace("{num_pods}", str(num_pods)))
        file = open(f"{self.out_dir}/extract_worker-{model_name}.yml", "w") 
        file.write(content) 
        file.close()  

    def gen(self, extra_data = None):
        for model in self.data["models"]:
            print(model)
            self.gen_from_template(model["name"], model["pods"], model.get("model_url", ""))

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
        print(self.data)
        for model in self.data["models"]:
            self.gen_from_template(model["name"], model["num_indexes"], model["pods"], model.get("index_algorithm", "brute"), model.get("model_url", ""))
        pass

class Serving(Common_generator):
    def __init__(self, data):
        super().__init__(data)
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
    
    def gen_from_template(self, model_name, num_indexes, model_url = ""):
        template_file = open(f"{self.template_dir}/serving.yml")
        content = template_file.read().replace("{model}", model_name).replace("{model_url}", model_url).replace("{num_indexes}", str(num_indexes))
                
        file = open(f"{self.out_dir}/serving-{model_name}.yml", "w") 
        file.write(content) 
        file.close() 


    def gen(self, extra_data = None):
        indexes = self.get_indexes_info(extra_data) 
        for model in self.models_data:
            model_name = model["name"]
            num_indexes = indexes.get(model_name, 0)
            if num_indexes == 0:
                print(f"ERROR: Could not found index service for model {model_name}")
                continue
            
            self.gen_from_template(model_name, num_indexes, model.get("model_url", ""))

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
            file = open(f"{self.out_dir}/mongo_config_db.sh", "w") 
            file.write(content) 
            file.close()
        
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
            model_names = [
                'vgg16',
                'vgg19',
                'mobilenet',
                'inception',
                'resnet',
                'xception'
            ]

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
            file = open(f"{self.out_dir}/mongo_shard.sh", "w") 
            file.write(content) 
            file.close()


        def gen(self, extra_data = None):
            self.gen_yml()
            self.gen_script()

    def __init__(self, data):
        super().__init__(data)
        self.sub_services = data["services"]
        self.generator_mappings = {
            "config_db": self.Config_db,
            "router": self.Router,
            "shard": self.Shard
        }

    def gen(self, extra_data = None):
        for sub_service in self.sub_services:
            generator = self.generator_mappings.get(sub_service["name"], Common_generator)(sub_service)
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
            "mongo": Mongo
        }

    def gen_service(self):
        services = self.data.get("services", [])
        for service in services:
            generator = self.get_generator(service)
            generator.gen(self.data)
    
    def get_generator(self, data):
        return self.generator_mappings.get(data["name"], Common_generator)(data)

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

    os.chdir("..")
    # execute("./build-docker-img.sh")
    os.chdir("configs")
    execute(f"rm -r {main_dir} && mv {stage_dir} {main_dir} && mkdir {stage_dir}  && oc apply -f {main_dir}")
    execute("sh expose.sh")

if __name__ == '__main__':
    if not os.path.exists(stage_dir):
        os.mkdir(stage_dir)
    
    if not os.path.exists(main_dir):
        os.mkdir(main_dir)

    generator = Generator("config.json")
    generator.gen_service()
    # clean_and_apply()
