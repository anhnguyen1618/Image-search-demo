import sys
import os
sys.path.append(os.path.abspath('../bucket'))
sys.path.append(os.path.abspath('../utilities'))

from bucket import Bucket
from utilities import allowed_file
from publisher import Publisher

class Ingestor:
    def __init__(self, bucket_name, queue_name):
        self.bucket = Bucket(bucket_name)
        self.bucket_name = bucket_name
        host_name = "localhost"
        queue_name = "images"
        self.publisher = Publisher({"hostname": host_name, "queue_name": queue_name})
    

    
    def read_dir(self, dir_path):
        return [f"{dir_path}/{file}" for file in os.listdir(dir_path) if allowed_file(file)]
    
    def upload_folder(self, dir_path):
        print(f"Begin uploading dir {dir_path}")
        file_names = self.read_dir(dir_path)
        for file_name in file_names:
            bucket_file_name = self.bucket.upload(file_name)
            self.publisher.publish(bucket_file_name)

        print(f"Done with uploading {len(file_names)} images to bucket {self.bucket_name}")

if __name__ == "__main__":
    BUCKET_NAME = "images-search"
    QUEUE_NAME = "images-search"

    ingestor = Ingestor(BUCKET_NAME, QUEUE_NAME)
    ingestor.upload_folder("../dataset")


