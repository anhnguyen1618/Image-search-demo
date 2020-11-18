import pika, sys, os
from pymongo import MongoClient


sys.path.append(os.path.abspath('../bucket'))
sys.path.append(os.path.abspath('../extractors'))

from bucket import Bucket
from extractors import model_picker, extract_features

class Worker:
    def __init__(self, params):
        queue_name = params["queue_name"]
        host_name = params.get("host_name", "localhost")
        mongo_address = params.get("mongo_address", "localhost:27017")
        self.bucket_name = params["bucket_name"]

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host_name)) 
        self.channel = self.connection.channel() 
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_qos(prefetch_count = 64)
        # set up subscription on the queue
        self.channel.basic_consume(queue_name, self.process)

        # start consuming (blocks)
        self.num_threads = 4
        self.model_name = queue_name
        
        self.bucket_handler = Bucket(bucket_name)

        # change model later
        self.model = model_picker('resnet')

        # set up db
        client = MongoClient(mongo_address)
        self.db = client.features
        
        self.channel.start_consuming()
        self.connection.close()   
    
    def get_public_url(self, file_name):
        return f"https://storage.googleapis.com/{self.bucket_name}/{file_name}" 
    
    def process(self, ch, method, properties, file_name):
        file_name = file_name.decode()
        print("file name", file_name)
        downloaded_dir = "../tmp"
        local_file_path = self.bucket_handler.download(file_name, downloaded_dir)
        feature = extract_features(local_file_path, self.model)
        self.db[self.model_name].insert_one({"url": self.get_public_url(file_name), "feature": feature.tolist()})
        print(feature)
        print("-------------------------------")
        self.channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    algorithm = "resnet"
    bucket_name = "images-search"
    mongo_address = "127.0.0.1:1048"
    Worker({"queue_name": algorithm, "bucket_name": bucket_name, "mongo_address": mongo_address})