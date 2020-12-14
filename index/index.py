import random
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from pymongo import MongoClient
from utilities import Logger

class Index:
    def __init__(self, mongo_address, model_name, total_indexes, current_index, n_neighbors=5, algorithm="brute", metric="euclidean"):
        self.logger = Logger()
        client = MongoClient(mongo_address)
        self.db = client.features

        self.records = self.load_data(model_name, total_indexes, current_index)
        features = list(map(lambda x: x["feature"], self.records))
        urls = list(map(lambda x: x["url"], self.records))
        self.logger.info(f"Indexing {len(urls)} records for model {model_name} using algorithm {algorithm}")
        self.neighbors = None
        if len(self.records):
            self.neighbors = NearestNeighbors(
                n_neighbors=min(n_neighbors, len(self.records)),
                algorithm=algorithm,
                metric=metric).fit(features)
            self.logger.info(f"Done indexing {len(self.records)} records")

    def load_data(self, model_name, total_indexes, current_index):
        total_num_of_records = self.db[model_name].count()
        num_of_records_per_index = int(total_num_of_records / max(total_indexes, 1))
        start_index = current_index * num_of_records_per_index
        self.logger.info(f"Load {num_of_records_per_index} / {total_num_of_records} records starting from index {start_index}")
        return list(self.db[model_name].find({}).skip(start_index).limit(num_of_records_per_index))

    def query(self, vector, n_neighbors = 5):
        if not self.neighbors:
            return []

        distances, indices = self.neighbors.kneighbors([vector], min(len(self.records), n_neighbors), return_distance = True)
        distances = distances[0]
        indices = indices[0]
        results = []
        for i in range(len(indices)):
            distance = distances[i]
            index = indices[i]
            url = self.records[index]["url"]
            results.append({"distance": distance, "url": url})
        return results

    def test(self):
        return self.records[1]["feature"]

if __name__ == '__main__':
    mongo_address = "mongos:27017"
    #mongo_address = "mongo_test:27017"
    model_name = "resnet"
    index = Index(mongo_address, model_name)
    # Change this
    vector = index.test()
    results = index.query(vector)
    print(results)
    pass




