import random
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import PIL
from PIL import Image
from sklearn.neighbors import NearestNeighbors
from pymongo import MongoClient

class Index:
    def __init__(self, mongo_address, model_name, n_neighbors=5, algorithm="brute", metric="euclidean"):
        client = MongoClient(mongo_address)
        self.db = client.features
        self.records = list(self.db[model_name].find({}))
        features = list(map(lambda x: x["feature"], self.records))
        if len(self.records):
            self.neighbors = NearestNeighbors(
                n_neighbors=n_neighbors,
                algorithm=algorithm,
                metric=metric).fit(features)
    
    def query(self, vector, n_neighbors = 5):
        if len(self.records) == 0:
            return []

        distances, indices = self.neighbors.kneighbors([vector], n_neighbors, return_distance = True)
        distances = distances[0]
        indices = indices[0]
        results = []
        for i in range(len(indices)):
            index = indices[i]
            distance = distances[i]
            url = self.records[i]["url"]
            results.append({"distance": distance, "url": url})
        return results
    
    def test(self):
        return self.records[0]["feature"]

if __name__ == '__main__':
    # mongo_address = "127.0.0.1:1048"
    mongo_address = "mongo_test:27017"
    model_name = "resnet"
    index = Index(mongo_address, model_name)
    # Change this
    vector = index.test()
    results = index.query(vector)
    print(results)
    pass






