from flask import Flask, abort, render_template, request
import uuid, os, json
from numpyencoder import NumpyEncoder
from extractor import model_picker, extract_features

app = Flask(__name__)

FILE_UPLOAD_DIR = os.getcwd() + "/files"
app = Flask(__name__, static_url_path = FILE_UPLOAD_DIR)
ALLOWED_EXTENSIONS = ["jpg", "png"]

model_name = 'resnet'
model = model_picker(model_name)

def allowed_file(filename):
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
        return json.dumps(feature_vector, cls=NumpyEncoder)
    
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