import json
import pika


class RabbitMqProvider:
    def __init__(self, host, port, username, password, queue_name):
        self.queue_name = queue_name
        port = int(port)
        self.connect = self.connect_to_rabbit(host, port, username, password)
        self.channel = self.connect.channel()
        self.channel_declare(self.channel, self.queue_name)


    def connect_to_rabbit(self, host, port, username, password):
        credentials = pika.PlainCredentials(username=username, password=password)
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                heartbeat_interval=6960))

    def channel_declare(self, channel, queue_name):
        channel.queue_declare(
            queue=queue_name,
            durable=True, arguments={
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': 'error-' + queue_name
            })

    def publish(self, message):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body = json.dumps(message, ensure_ascii=False).encode('utf-8'),
            properties=pika.BasicProperties(delivery_mode=2))
        print('Publish message to queue ' + self.queue_name)