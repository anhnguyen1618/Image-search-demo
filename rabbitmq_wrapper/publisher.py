import pika

class Publisher:
    def __init__(self, params):
        queue_name = params["queue_name"]
        host_name = params.get("rabbitmq_hostname", "localhost")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host_name)) # Connect to CloudAMQP
        self.channel = self.connection.channel() # start a channel
        self.channel.queue_declare(queue = queue_name)
        self.queue_name = queue_name
    
    def close(self):
        self.connection.close()
    
    def publish(self, file_name):
        self.channel.basic_publish(exchange = '', routing_key = self.queue_name, body = file_name)


