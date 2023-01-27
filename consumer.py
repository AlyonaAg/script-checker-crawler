from kafka import KafkaConsumer
import sys
import const


class Consumer:
    def __init__(self, topic, broker):
        self.consumer = KafkaConsumer(topic, bootstrap_servers=broker, api_version=(0,10))

    def reciver(self):
        try:
            for message in self.consumer:
                print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key,message.value))
        except KeyboardInterrupt:
            sys.exit()