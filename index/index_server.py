from index import Index
import json
from flask import Flask, request

app = Flask(__name__)

print("run in to main here")
mongo_address = "mongo_test:27017"
# mongo_address = "127.0.0.1:1048"
model_name = "resnet"
index = Index(mongo_address, model_name)

@app.route("/")
def hello():
    return "tests"

@app.route("/search", methods=["POST"])
def search():
    print("run into search")
    results = index.query(request.get_json())
    # results = index.query(index.test())
    # print("index results", results)
    return json.dumps(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)