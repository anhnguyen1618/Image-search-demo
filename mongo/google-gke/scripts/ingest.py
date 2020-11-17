import csv
import os
from pymongo import MongoClient
import time
import math

# DB connections
def get_mongo_url():
    urls = os.getenv("MONGO_ADDR") and os.environ["MONGO_ADDR"] or os.popen("minikube service mongos --url").read()
    url = urls.strip('\n')
    parts = url.split(":")
    host_name = parts[1].strip('//')
    port_number = int(parts[2])

    return {"url": url, "host_name": host_name, "port_number": port_number}

mongo_addr = get_mongo_url()
client = MongoClient(mongo_addr["host_name"], mongo_addr["port_number"])
db = client.test
record_collections = db.records


FILE_PATH = '2018_Yellow_Taxi_Trip_Data.csv'
NUM_RECORD_IN_BATCH = 2000

def construct_document(row):
    title_mappings = [
            'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'Passenger_count', 'Trip_distance', 'RatecodeID', 'store_and_fwd_flag','PULocationID', 'DOLocationID', 'Payment_type', 'Fare_amount', 'Extra', 'MTA_tax', 'Tip_amount', 'Tolls_amount', 'improvement_surcharge', 'Total_amount']

    dict = {}
    for index in range(len(row)):
        dict[title_mappings[index]] = row[index]
    return dict
    

def ingest(file_path):
    with open(file_path) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')

        pass_first_title_line = False
        start_time = time.time()
        total = 0
        fail = 0

        # a batch of size 2000 records to insert to mongo in one request
        buffers = []

        for row in readCSV:
            if pass_first_title_line == False:
                pass_first_title_line = True
                continue

            buffers.append(construct_document(row))
            total += NUM_RECORD_IN_BATCH

            if total % NUM_RECORD_IN_BATCH == 0:
                try:
                    result = record_collections.insert_many(buffers)
                    buffers = []
                except Exception as e:
                    print(e)
                    buffers = []
                    fail += NUM_RECORD_IN_BATCH
        
        # Handle case where buffers are not empty at the end
        if len(buffers):
            try:
                total += len(buffers)
                result = record_collections.insert_many(buffers)
                buffers = []
            except Exception as e:
                print(e)
                fail += len(buffers)
                buffers = []

        end_time = time.time()
        print("fail rate: ", fail * 100.0 / total)
        print("total time: ", math.floor(end_time - start_time), "s")

def main():
    ingest(FILE_PATH)

if __name__== "__main__":
    main()

