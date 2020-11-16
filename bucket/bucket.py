from google.cloud import storage
import uuid, os, string, sys

sys.path.append(os.path.abspath('../utilities'))
from utilities import uniq_file_name

class Bucket:
    def __init__(self, bucket_name):
        storage_client = storage.Client()
        self.bucket = storage_client.get_bucket(bucket_name)

    def upload(self, file_name):
        local_file = file_name
        bucket_file_name = uniq_file_name(file_name)
        blob = self.bucket.blob(bucket_file_name)
        blob.upload_from_filename(local_file)
        return bucket_file_name 

    def download(self, file_name, local_downloaded_dir):
        blob = bucket.blob(file_name)
        if blob.exists():
            file_loc = os.path.join(local_downloaded_dir, file_name)
            blob.download_to_filename(file_loc)