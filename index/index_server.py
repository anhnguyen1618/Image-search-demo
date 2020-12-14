from index import Index
import json, os
from flask import Flask, request, Response
import prometheus_client
from prometheus_client import start_http_server, Summary, Counter, Gauge
from utilities import Logger

app = Flask(__name__)

TOTAL_NUM_INDEXES = int(os.getenv('TOTAL_NUM_INDEXES', 1))
CURRENT_INDEX = int(os.getenv('CURRENT_INDEX', 1)) - 1
ML_MODEL = os.getenv('ML_MODEL', "resnet")
index_algorithm = os.getenv('INDEX_ALGORITHM', "brute")

mongo_address = "mongos:27017"
# mongo_address = "127.0.0.1:1048"
model_name = ML_MODEL 
index = None 

logger = Logger()

class Observer:
    def __init__(self):
        self.request_time = Summary('index_processing_duration', 'Time spent indexing')
        self.failure_count = Counter('num_of_exception', 'Number of exception')
        self.index_gauge = Gauge("num_index_record", "Number of indexed records")
        self.search_time = Summary("index_search_duration", "Time spent in searching")
    def gen_report(self):
        return [ prometheus_client.generate_latest(v) for v in [self.request_time, self.failure_count, self.index_gauge, self.search_time] ]

observer = Observer()

@app.route("/")
def hello():
    return "tests"

@app.route("/reindex")
@observer.failure_count.count_exceptions()
@observer.request_time.time()
def reindex():
    global index
    index = Index(mongo_address, model_name, TOTAL_NUM_INDEXES, CURRENT_INDEX, algorithm = index_algorithm)
    msg = f"Done indexing {len(index.records)}"
    observer.index_gauge.set(len(index.records))
    return msg 

@app.route("/search", methods=["POST"])
@observer.failure_count.count_exceptions()
@observer.search_time.time()
def search():
    results = index.query(request.get_json())
    return json.dumps(results)

@app.route("/metrics")
def metrics():
    return Response(observer.gen_report(), mimetype="text/plain")

# if __name__ == "__main__":
#     reindex()
#     app.run(host='0.0.0.0', port=5000, debug=True)