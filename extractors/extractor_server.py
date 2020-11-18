from flask import Flask, abort, render_template, request
import requests
import uuid, os, json
from numpyencoder import NumpyEncoder
from extractors import model_picker, extract_features


FILE_UPLOAD_DIR = os.getcwd() + "/files"
INDEX_URL = "http://indexing:5000"
model_name = 'resnet'
model = model_picker(model_name)

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
        res = requests.post(INDEX_URL+"/search", json=payload)
        return render_template("index.html", results = res.json())
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