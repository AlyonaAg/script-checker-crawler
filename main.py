import consumer
import const
import producer
import argparse

parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
parser.add_argument('-c', action='store_true')
parser.add_argument('-l', action='store_true')

args = parser.parse_args()

p = producer.Producer(const.result_topic, const.bootstrap_servers)
c = consumer.Consumer(const.original_script_topic, const.bootstrap_servers, p, args.c, args.l)
c.reciver()