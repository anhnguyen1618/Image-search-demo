import pika, sys, os
from pymongo import MongoClient
import time
import requests
from prometheus_client import start_http_server, Summary, Counter

sys.path.append(os.path.abspath('../bucket'))
sys.path.append(os.path.abspath('../extractors'))
from bucket import Bucket
from extractors import model_picker, extract_features
from utilities import Logger

REQUEST_TIME = Summary('extract_worker_processing_duration', 'Time spent processing 1 image')
FAILURE_COUNTER = Counter('number_of_exception', 'Number of exception')

class Worker:
    def __init__(self, params):
        queue_name = params["queue_name"]
        model_url = params["model_url"]
        host_name = params.get("rabbitmq_hostname", "localhost")
        mongo_address = params.get("mongo_address", "localhost:27017")
        self.bucket_name = params["bucket_name"]
        self.deduplicate_model = params["deduplicate_model"]
        self.deduplicate_threshold = params["deduplicate_threshold"]
        self.logger = Logger()

        while True:
            try:
                if self.set_up_rabbitmq_connection(host_name, queue_name):
                    break
            except Exception as e:
                self.logger.error(f"Failed to connect to rabbitmq queue {queue_name} at {host_name}. Reason: {e}")
                time.sleep(3)
                continue

        # start consuming (blocks)
        self.num_threads = 4
        self.model_name = queue_name
        
        self.bucket_handler = Bucket(bucket_name)

        self.logger.info(f"Extract worker for model: {queue_name}")
        self.model = model_picker(queue_name, model_url)

        self.logger.info(f"Connecting to mongodb at {mongo_address}")
        client = MongoClient(mongo_address)
        self.db = client.features
        
        self.channel.start_consuming()
        self.connection.close()   
    
    def set_up_rabbitmq_connection(self, host_name, queue_name):
        credentials = pika.PlainCredentials('admin', 'admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host_name, credentials=credentials)) 
        self.channel = self.connection.channel() 
        self.channel.queue_declare(queue=queue_name)
        self.channel_name = "features"
        self.channel.exchange_declare(exchange=self.channel_name, exchange_type="fanout")
        self.channel.queue_bind(exchange=self.channel_name,
                   queue=queue_name)
        self.channel.basic_qos(prefetch_count = 20)
        # set up subscription on the queue
        self.channel.basic_consume(queue_name, self.process)
        return True
    
    def get_public_url(self, file_name):
        return f"https://storage.googleapis.com/{self.bucket_name}/{file_name}" 
    
    def check_duplication(self, img_name, feature):
        response = requests.post(f"http://serving-{self.deduplicate_model}:5000/search?json=true", json=feature.tolist()) 
        if response.status_code != 200:
            print(f"Deduplicate request fails for image {img_name}")
            return False 
        result = response.json()

        if len(result) == 0:
            return False
        
        best_match = result[0]["distance"]
        is_duplicated = best_match <= self.deduplicate_threshold
        if is_duplicated:
            print(f"Image {img_name} already exists")
            self.channel.basic_publish(exchange = "", routing_key = "duplicated_files", body = img_name)
        return is_duplicated


    @FAILURE_COUNTER.count_exceptions()
    @REQUEST_TIME.time()
    def process(self, ch, method, properties, file_name):
        file_name = file_name.decode()
        print(f"Processing file {file_name}")
        downloaded_dir = "./tmp"
        local_file_path = self.bucket_handler.download(file_name, downloaded_dir)
        feature = extract_features(local_file_path, self.model)

        if self.deduplicate_model:
            is_duplicated = self.check_duplication(file_name, feature)
            if is_duplicated:
                self.channel.basic_ack(delivery_tag=method.delivery_tag)      
                return

        self.db[self.model_name].insert_one({"url": self.get_public_url(file_name), "feature": feature.tolist()})
        self.channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    ML_MODEL = os.getenv('ML_MODEL', "resnet")
    algorithm = ML_MODEL 
    MODEL_URL = os.getenv("MODEL_URL", "")
    DEDUPLICATE_MODEL = "" #os.getenv("DEDUPLICATE_MODEL", "mobilenet")
    DEDUPLICATE_THRESHOLD = "" #float(os.getenv("DEDUPLICATE_THRESHOLD", 0))

    bucket_name = "images-search"
    # mongo_address = "mongo_test:27017" 
    mongo_address = "mongos:27017" 
    rabbitmq_hostname = "rabbitmq"
    start_http_server(5000)
    Worker({
        "queue_name": algorithm,
        "model_url": MODEL_URL,
        "bucket_name": bucket_name,
        "mongo_address": mongo_address,
        "rabbitmq_hostname": rabbitmq_hostname,
        "deduplicate_model": DEDUPLICATE_MODEL,
        "deduplicate_threshold": DEDUPLICATE_THRESHOLD
        })
