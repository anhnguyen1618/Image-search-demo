import pika

class Publisher:
    def __init__(self, params):
        host_name = params.get("rabbitmq_hostname", "localhost")
        self.exchange_name = "features"
        credentials = pika.PlainCredentials('admin', 'admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host_name, credentials=credentials)) 
        self.channel = self.connection.channel() # start a channel
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="fanout")
    
    def close(self):
        self.connection.close()
    
    def publish(self, file_name):
        self.channel.basic_publish(exchange = self.exchange_name, routing_key = "", body = file_name)


