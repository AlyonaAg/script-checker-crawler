from kafka import KafkaProducer
import json


class Producer:
    def __init__(self, topic, broker):
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=broker, api_version=(0,10), value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def send(self, id, result):
        self.producer.send(self.topic, {'id': id, 'result':result})