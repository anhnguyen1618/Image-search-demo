import pika, sys, os
from pymongo import MongoClient
import time

sys.path.append(os.path.abspath('../bucket'))
sys.path.append(os.path.abspath('../extractors'))
from bucket import Bucket
from extractors import model_picker, extract_features

class Worker:
    def __init__(self, params):
        queue_name = params["queue_name"]
        host_name = params.get("rabbitmq_hostname", "localhost")
        mongo_address = params.get("mongo_address", "localhost:27017")
        self.bucket_name = params["bucket_name"]

        while True:
            try:
                if self.set_up_rabbitmq_connection(host_name, queue_name):
                    break
            except Exception as e:
                print(e)
                time.sleep(3)
                continue

        # start consuming (blocks)
        self.num_threads = 4
        self.model_name = queue_name
        
        self.bucket_handler = Bucket(bucket_name)

        print(f"Extract worker for model: {queue_name}")
        # change model later
        self.model = model_picker(queue_name)

        # set up db
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
    
    def process(self, ch, method, properties, file_name):
        file_name = file_name.decode()
        print("file name", file_name)
        downloaded_dir = "./tmp"
        local_file_path = self.bucket_handler.download(file_name, downloaded_dir)
        feature = extract_features(local_file_path, self.model)
        self.db[self.model_name].insert_one({"url": self.get_public_url(file_name), "feature": feature.tolist()})
        print("-------------------------------")
        self.channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    ML_MODEL = os.getenv('ML_MODEL', "resnet")
    algorithm = ML_MODEL 
    bucket_name = "images-search"
    # mongo_address = "mongo_test:27017" 
    mongo_address = "mongos:27017" 
    rabbitmq_hostname = "rabbitmq"
    Worker({"queue_name": algorithm, "bucket_name": bucket_name, "mongo_address": mongo_address, "rabbitmq_hostname": rabbitmq_hostname})
