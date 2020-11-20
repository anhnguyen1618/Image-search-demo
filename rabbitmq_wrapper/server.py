import json, pika
from flask import Flask, request

from publisher import Publisher 

app = Flask(__name__)

rabbitmq_hostname = "rabbitmq"

@app.route("/", methods=["POST"])
def publish():
    payload = request.get_json()
    print(request.data)
    img_url = payload["url"]
    queue_name = payload["queue_name"]

    publisher = Publisher({
            "rabbitmq_hostname": rabbitmq_hostname,
            "queue_name": queue_name
        })
    publisher.publish(img_url)
    return "done" 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)