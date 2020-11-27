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
    def gen_from_template(self, model_name, num_pods):
        template_file = open(f"{self.template_dir}/extract_worker.yml")
        template_content = template_file.read()
        content = (
            template_content
            .replace("{model}", model_name)
            .replace("{num_pods}", str(num_pods)))
        file = open(f"{self.out_dir}/extract_worker-{model_name}.yml", "w") 
        file.write(content) 
        file.close()  

    def gen(self, extra_data = None):
        for model in self.data["models"]:
            self.gen_from_template(model["name"], model["pods"])

class Indexing(Common_generator):
    def gen_from_template(self, model_name, num_indexes, num_pods):
        template_file = open(f"{self.template_dir}/indexing.yml")
        template_content = template_file.read()
        for index_num in range(1, num_indexes + 1):
            content = (
                template_content
                .replace("{model}", model_name)
                .replace("{num_indexes}", str(num_indexes))
                .replace("{index_num}", str(index_num))
                .replace("{num_pods}", str(num_pods)))
            file = open(f"{self.out_dir}/indexing-{model_name}-{index_num}.yml", "w") 
            file.write(content) 
            file.close() 
        
    def gen(self, extra_data = None):
        print(self.data)
        for model in self.data["models"]:
            print("model")
            self.gen_from_template(model["name"], model["num_indexes"], model["pods"])
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
    
    def gen_from_template(self, model_name, num_indexes):
        template_file = open(f"{self.template_dir}/serving.yml")
        content = template_file.read().replace("{model}", model_name).replace("{num_indexes}", str(num_indexes))
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
            
            self.gen_from_template(model_name, num_indexes)
    

class Generator:
    def __init__(self, path):
        file = open(path)
        self.data = json.load(file)
        self.generator_mappings = {
            "extract_worker": Extract_worker,
            "indexing": Indexing,
            "serving": Serving
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

if __name__ == '__main__':
    if not os.path.exists(stage_dir):
        os.mkdir(stage_dir)
    
    if not os.path.exists(main_dir):
        os.mkdir(main_dir)

    generator = Generator("config.json")
    generator.gen_service()
    clean_and_apply()
