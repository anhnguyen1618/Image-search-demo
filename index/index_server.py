from index import Index
import json, os
from flask import Flask, request

app = Flask(__name__)

TOTAL_NUM_INDEXES = int(os.getenv('TOTAL_NUM_INDEXES', 1))
CURRENT_INDEX = int(os.getenv('CURRENT_INDEX', 1)) - 1
ML_MODEL = os.getenv('ML_MODEL', "resnet")
index_algorithm = os.getenv('INDEX_ALGORITHM', "brute")

mongo_address = "mongos:27017"
# mongo_address = "127.0.0.1:1048"
model_name = ML_MODEL 
index = Index(mongo_address, model_name, TOTAL_NUM_INDEXES, CURRENT_INDEX, algorithm=index_algorithm)

@app.route("/")
def hello():
    return "tests"

@app.route("/reindex")
def reindex():
    global index
    index = Index(mongo_address, model_name, TOTAL_NUM_INDEXES, CURRENT_INDEX)
    msg = f"Done indexing {len(index.records)}"
    return msg 

@app.route("/search", methods=["POST"])
def search():
    print("run into search")
    results = index.query(request.get_json())
    # results = index.query(index.test())
    # print("index results", results)
    return json.dumps(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)