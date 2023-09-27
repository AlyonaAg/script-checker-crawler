from kafka import KafkaConsumer
import sys
import packer_detector.packer_detector
from pymarshaler.marshal import Marshal
import json
import requests
from dataclasses import dataclass


@dataclass
class Script: 
    id: int
    script: str


class Consumer:
    def __init__(self, topic, broker, sender, collect_mode=False, label=False):
        self.consumer = KafkaConsumer(topic, bootstrap_servers=broker, api_version=(0,10))
        self.marshal = Marshal()
        self.sender = sender
        self.collect_mode = collect_mode
        self.label = label

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
        if not msg_unmarshal.script.startswith('file://'):
            # print('website script')
            response = requests.get(msg_unmarshal.script)
            text = response.text
        else:
            # print('file script')
            path = msg_unmarshal.script[len('file://'):]
            print('PATH: ', path)

            with open(path, 'r') as fp:
                text = fp.read()

        res = packer_detector.packer_detector.scan_script(text, self.collect_mode, self.label)
            

        print('Obfuscate: ', res)

        self.sender.send(msg_unmarshal.id, res)