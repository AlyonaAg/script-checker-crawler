import consumer
import const


c = consumer.Consumer(const.original_script_topic, const.bootstrap_servers)
c.reciver()