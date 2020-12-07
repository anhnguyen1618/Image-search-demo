import json, pika, time
from flask import Flask, request, Response
import prometheus_client
from prometheus_client import Counter, Histogram
from prometheus_client.core import CollectorRegistry


from publisher import Publisher 

app = Flask(__name__)

def connect_to_queue(rabbitmq_hostname):
    publisher = None
    while not publisher:
        try:
            print(f"Connecting to rabbitmq at '{rabbitmq_hostname}'")
            publisher = Publisher({
                "rabbitmq_hostname": rabbitmq_hostname
            })
        except Exception as e:
            print(f"Failed to connect to rabbitmq at hostname '{rabbitmq_hostname}''")
            print(e)
            time.sleep(2)
    print(f"Connected to rabbitmq at '{rabbitmq_hostname}'")
    return publisher

rabbitmq_hostname = "rabbitmq"
publisher = connect_to_queue(rabbitmq_hostname)

class Observer:
    def __init__(self):
        self.metrics = {}
        self.metrics["received_msgs"] = Counter("received_msgs", "Total number of messages received")
        self.metrics["run_time"] = Histogram('run_time', 'Histogram for the duration in mili seconds.', buckets=(1, 2, 5, 6, 10, float("inf"))) 
        self.metrics["processed_msgs"] = Counter("processed_msgs", "Total number of processed messages")

    def inc(self, metric_type):
        self.metrics[metric_type].inc()

    def start_timer(self):
        self.start = time.time()
    
    def end_timer(self):
        duration = 1000 *(time.time() - self.start)
        self.metrics["run_time"].observe(duration)
    
    def gen_report(self):
        return [ prometheus_client.generate_latest(v) for _, v in self.metrics.items() ]

observer = Observer()

@app.route("/", methods=["POST"])
def publish():
    observer.start_timer()
    observer.inc("received_msgs")

    payload = request.get_json()
    img_url = payload["url"]
    publisher.publish(img_url)

    observer.inc("processed_msgs")
    observer.end_timer()
    return "done"

@app.route("/metrics")
def collect():
    return Response(observer.gen_report(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)