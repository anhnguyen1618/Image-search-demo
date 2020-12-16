import json, pika, time
from flask import Flask, request, Response
import prometheus_client
from prometheus_client import Counter, Summary 
from prometheus_client.core import CollectorRegistry

from utilities import Logger
from publisher import Publisher 

logger = Logger()

app = Flask(__name__)

# def connect_to_queue(rabbitmq_hostname):
#     publisher = None
#     while not publisher:
#         try:
#             print(f"Connecting to rabbitmq at '{rabbitmq_hostname}'")
#             publisher = Publisher({
#                 "rabbitmq_hostname": rabbitmq_hostname
#             })
#         except Exception as e:
#             print(f"Failed to connect to rabbitmq at hostname '{rabbitmq_hostname}''")
#             print(e)
#             time.sleep(2)
#     print(f"Connected to rabbitmq at '{rabbitmq_hostname}'")
#     return publisher
# publisher = connect_to_queue(rabbitmq_hostname)

rabbitmq_hostname = "rabbitmq"

class Observer:
    def __init__(self):
        self.metrics = {}
        self.received_msgs = Counter("received_msgs", "Total number of messages received")
        self.run_time = Summary("rabbitmq_wrapper_forward_duration", "Time spent in forwarding messages")
        self.processed_msgs = Counter("forward_msgs", "Total number of forwarded messages")
        self.failure_count = Counter('num_of_exception', 'Number of exception')
    
    def gen_report(self):
        return [ prometheus_client.generate_latest(v) for v in [self.received_msgs, self.run_time, self.processed_msgs, self.failure_count] ]

observer = Observer()

@observer.run_time.time()
@observer.failure_count.count_exceptions()
@app.route("/", methods=["POST"])
def publish():
    observer.received_msgs.inc()

    payload = request.get_json()
    img_url = payload["url"]
    queue_name = payload.get("queue_name", "")
    publisher = Publisher({ "rabbitmq_hostname": rabbitmq_hostname })
    publisher.publish(img_url, queue_name)

    observer.processed_msgs.inc()
    return f"Sent {img_url} to {('exchange ' +  publisher.exchange_name) if not queue_name else queue_name}"

@app.route("/metrics")
def collect():
    return Response(observer.gen_report(), mimetype="text/plain")


# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)