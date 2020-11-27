from flask import Flask, abort, render_template, request
import requests, asyncio
import uuid, os, json
from numpyencoder import NumpyEncoder
from extractors import model_picker, extract_features

TOTAL_NUM_INDEXES = int(os.getenv('TOTAL_NUM_INDEXES', 1))
# TODO: use model to fetch correct service later
ML_MODEL = os.getenv('ML_MODEL', "resnet")

FILE_UPLOAD_DIR = os.getcwd() + "/files"
INDEX_URL = f"http://indexing-{ML_MODEL}"
PORT=5000

model = model_picker(ML_MODEL)

app = Flask(__name__, static_url_path = FILE_UPLOAD_DIR)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ["jpg", "png", "jpeg"]
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    file = request.files['record']
    file_name = str(uuid.uuid1()) + "." + file.filename.rsplit('.', 1)[1].lower()
    file_path = os.path.join(FILE_UPLOAD_DIR, file_name)
    file.save(file_path)
    return file_path

async def aggregate(payload, res):
    # res = requests.post(INDEX_URL+"/search", json=payload)
    results = []
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(
            None, 
            requests.post,
            f"{INDEX_URL}-{index}:{PORT}/search",
            None,
            payload
        )
        for index in range(1, TOTAL_NUM_INDEXES + 1)
    ]
    for response in await asyncio.gather(*futures):
        if response.status_code != 200:
            print(f"Error fetching results from {response.url}")
            continue

        results += response.json()
        print(response.json(), flush=True)
        
    res["results"] = results 

def search_from_index(payload, num_records=5):
    loop = asyncio.new_event_loop()
    res = {"results":[]}
    loop.run_until_complete(aggregate(payload, res))
    res["results"].sort(key=lambda x: x["distance"])
    return res["results"][:num_records]


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    if request.files and request.files['record'] and allowed_file(request.files['record'].filename): 
        file = request.files['record']
        path = save_file(file)
        feature_vector = extract_features(path, model)

        # payload = json.dumps(feature_vector, cls=NumpyEncoder)
        payload = feature_vector.tolist()

        results = search_from_index(payload)
        return render_template("index.html", results = results)
        # return res.content
    
    return "file format is not acceptable", 500


@app.route("/changemodel/<new_model_name>")
def changemodel(new_model_name):
    new_model = model_picker(new_model_name) 
    if not new_model:
        abort(404)
        return 

    model = new_model
    model_name = new_model_name
    msg = f"Changed model from {model_name} to {new_model_name}"
    print(msg)

    return msg

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)