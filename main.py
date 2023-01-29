import consumer
import const
import producer

p = producer.Producer(const.result_topic, const.bootstrap_servers)
c = consumer.Consumer(const.original_script_topic, const.bootstrap_servers, p)
c.reciver()