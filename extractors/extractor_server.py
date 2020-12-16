from flask import Flask, abort, render_template, request, Response
import requests, asyncio
import uuid, os, json, time
from extractors import model_picker, extract_features
import prometheus_client
from prometheus_client import start_http_server, Summary, Counter
from utilities import Logger

logger = Logger()
TOTAL_NUM_INDEXES = int(os.getenv('TOTAL_NUM_INDEXES', 1))
ML_MODEL = os.getenv('ML_MODEL', "resnet")

FILE_UPLOAD_DIR = os.getcwd() + "/tmp"
INDEX_URL = f"http://indexing-{ML_MODEL}"
PORT=5000

# https://storage.googleapis.com/images-search/model-finetuned.h5
MODEL_URL = os.getenv('MODEL_URL', "")
model = model_picker(ML_MODEL, MODEL_URL)

app = Flask(__name__, static_url_path = FILE_UPLOAD_DIR)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ["jpg", "png", "jpeg"]
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def aggregate(payload, res, size = 10):
    # res = requests.post(INDEX_URL+"/search", json=payload)
    results = []
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(
            None, 
            requests.post,
            f"{INDEX_URL}-{index}:{PORT}/search?size={size}",
            None,
            payload
        )
        for index in range(1, TOTAL_NUM_INDEXES + 1)
    ]
    for response in await asyncio.gather(*futures):
        if response.status_code != 200:
            print("Error")
            # logger.error(f"Error fetching results from {response.url}")
            continue

        results += response.json()
        
    res["results"] = results 

class Observer:
    def __init__(self):
        self.request_time = Summary('serving_processing_duration', 'Time spent indexing')
        self.failure_count = Counter('serving_num_of_exception', 'Number of exception')
        self.search_time = Summary("serving_search_duration", "Time spent in searching")
        self.save_file_time= Summary("serving_save_file_duration", "Time spent in saving file")
        self.eval_model_time= Summary("serving_eval_model_duration", "Time spent in saving file")

    def gen_report(self):
        return [ prometheus_client.generate_latest(v) for v in [self.request_time, self.failure_count, self.search_time, self.save_file_time, self.eval_model_time] ]

observer = Observer()

@observer.save_file_time.time()
def save_file(file):
    file = request.files['record']
    file_name = str(uuid.uuid1()) + "." + file.filename.rsplit('.', 1)[1].lower()
    file_path = os.path.join(FILE_UPLOAD_DIR, file_name)
    file.save(file_path)
    return file_path

@observer.search_time.time()
def search_from_index(payload, num_records=15):
    loop = asyncio.new_event_loop()
    res = {"results":[]}
    loop.run_until_complete(aggregate(payload, res, num_records))
    res["results"].sort(key=lambda x: x["distance"])
    return res["results"][:num_records]

@observer.eval_model_time.time()
def extract_features_wrapper(path, model):
    return extract_features(path, model).tolist()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
@observer.failure_count.count_exceptions()
@observer.request_time.time()
def search():
    use_json = request.args.get('json', type=bool)
    size= request.args.get('size', type=int) or 10

    if request.files and request.files['record'] and allowed_file(request.files['record'].filename): 
        file = request.files['record']
        path = save_file(file)
        payload = extract_features_wrapper(path, model)
        results = search_from_index(payload, size) 

        return json.dumps(results) if use_json else render_template("index.html", results = results)
    
    return "file format is not acceptable", 500

@app.route("/changemodel/<new_model_name>")
def changemodel(new_model_name):
    global model
    new_model = model_picker(new_model_name) 
    if not new_model:
        abort(404)
        return 

    model = new_model
    model_name = new_model_name
    msg = f"Changed model from {model_name} to {new_model_name}"

    return msg

@app.route("/metrics")
def metrics():
    return Response(observer.gen_report(), mimetype="text/plain")

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000)