import sys, os, json, requests

sys.path.append(os.path.abspath('../bucket'))
sys.path.append(os.path.abspath('../utilities'))

from bucket import Bucket
from utilities import allowed_file


class Ingestor:
    def __init__(self, bucket_name, rabbitmq_url, queue_name):
        self.bucket = Bucket(bucket_name)
        self.bucket_name = bucket_name
        self.rabbitmq_url = rabbitmq_url
        self.queue_name = queue_name

    def read_dir(self, dir_path):
        return [
            f"{dir_path}/{file}" for file in os.listdir(dir_path)
            if allowed_file(file)
        ]

    def upload_folder(self, dir_path):
        print(f"Begin uploading dir {dir_path}")
        file_names = self.read_dir(dir_path)
        for file_name in file_names:
            bucket_file_name = self.bucket.upload(file_name)
            requests.post(self.rabbitmq_url,
                          json={
                              "url": bucket_file_name,
                              "queue_name": self.queue_name
                          })

        print(
            f"Done with uploading {len(file_names)} images to bucket {self.bucket_name}"
        )


if __name__ == "__main__":
    BUCKET_NAME = "images-search"
    model_name = "resnet"
    QUEUE_NAME = model_name
    RABBITMQ_URL = "http://rabbitmq-wrapper-mongo.rahtiapp.fi"
    # RABBITMQ_URL = "http://localhost:8000"

    ingestor = Ingestor(BUCKET_NAME, RABBITMQ_URL, QUEUE_NAME)
    data_dir = "../dataset"
    # data_dir = "../sample"
    # data_dir = "../test"
    ingestor.upload_folder(data_dir)
