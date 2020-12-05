import random
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import PIL
from PIL import Image
from sklearn.neighbors import NearestNeighbors
from pymongo import MongoClient

class Index:
    def __init__(self, mongo_address, model_name, total_indexes, current_index, n_neighbors=5, algorithm="brute", metric="euclidean"):
        client = MongoClient(mongo_address)
        self.db = client.features

        self.records = self.load_data(model_name, total_indexes, current_index)
        # self.records = list(self.db[model_name].find({}))
        features = list(map(lambda x: x["feature"], self.records))
        urls = list(map(lambda x: x["url"], self.records))
        print(f"Indexing {len(urls)} records for model {model_name} using algorithm {algorithm}")

        if len(self.records):
            self.neighbors = NearestNeighbors(
                n_neighbors=min(n_neighbors, len(self.records)),
                algorithm=algorithm,
                metric=metric).fit(features)

    def load_data(self, model_name, total_indexes, current_index):
        total_num_of_records = self.db[model_name].count()
        num_of_records_per_index = int(total_num_of_records / max(total_indexes, 1))
        return list(self.db[model_name].find({}).skip(current_index * num_of_records_per_index).limit(num_of_records_per_index))

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




