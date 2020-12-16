import sys, os, json, requests
import argparse

sys.path.append(os.path.abspath('../bucket'))
sys.path.append(os.path.abspath('../utilities'))

from bucket import Bucket
from utilities import allowed_file


result_size = 30 
relevant = 10



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
        counter = 0
        for file_name in file_names:
            bucket_file_name = self.bucket.upload(file_name)
            x = requests.post(self.rabbitmq_url,
                              json={
                                  "url": bucket_file_name,
                                  "queue_name": self.queue_name
                              })
            if x.status_code != 200:
                print(x.status_code)
                print(x.reason)
                print(f"Request fails for image: {bucket_file_name}")

            counter += 1
            if counter % 100 == 0:
                print(f"Uploaded {counter}/{len(file_names)} files !!!")

        print(
            f"Done with uploading {len(file_names)} images to bucket {self.bucket_name}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bucket", type=str, help="Google bucket name")
    parser.add_argument("-q", "--queue", type=str, help="Queue name")
    parser.add_argument("-d", "--dir", type=str, help="Dir to upload")
    args = parser.parse_args()
    BUCKET_NAME = args.bucket or "images-search"
    QUEUE_NAME = args.queue or "resnet" 

    # data_dir = "../dataset"
    # data_dir = "../dataset-10"
    data_dir = "../sample"

    DATA_DIR = args.dir or data_dir 
    RABBITMQ_URL = "http://rabbitmq-wrapper-mongo.rahtiapp.fi"
    # RABBITMQ_URL = "http://localhost:8000"
    ingestor = Ingestor(BUCKET_NAME, RABBITMQ_URL, QUEUE_NAME)
    ingestor.upload_folder(data_dir)
