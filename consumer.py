from kafka import KafkaConsumer
import sys
import const
import packer_detector.packer_detector
from pymarshaler.marshal import Marshal
import json
import base64
import requests
from dataclasses import dataclass


@dataclass
class Script: 
    id: int
    script: str


class Consumer:
    def __init__(self, topic, broker):
        self.consumer = KafkaConsumer(topic, bootstrap_servers=broker, api_version=(0,10))
        self.marshal = Marshal()

    def reciver(self):
        try:
            for message in self.consumer:
                print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key,message.value))
                try:
                    self.prepare_msg(message.value)
                except Exception as e:
                    print(e)
        except KeyboardInterrupt:
            sys.exit()

    def prepare_msg(self, msg):
        msg_unmarshal = self.marshal.unmarshal(Script, json.loads(msg))
        response = requests.get(msg_unmarshal.script)
        packer_detector.packer_detector.scan_script(response.text)