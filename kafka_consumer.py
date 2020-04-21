import time

from kafka import KafkaConsumer
from locust import events


class KafkaMessageConsumer:

    def __init__(self, kafka_brokers=None, topic_name=None, state_map=None):

        if kafka_brokers is None:
            kafka_brokers = ['localhost:9092']
        self.consumer = KafkaConsumer(
            topic_name, bootstrap_servers=kafka_brokers, group_id="test")
        self.state_map = state_map

    def consume(self):
        for message in self.consumer:

            consumed_at_time_millis = time.time()*1000
            produced_at_time_millis = self.state_map.get(
                message.key, consumed_at_time_millis)

            total_time = consumed_at_time_millis-float(produced_at_time_millis)

            request_data = dict(request_type="EVENT",
                                name="service-throughput",
                                response_time=total_time,
                                response_length=1)

            self.__fire_success(**request_data)

    def __fire_failure(self, **kwargs):
        events.request_failure.fire(**kwargs)

    def __fire_success(self, **kwargs):
        events.request_success.fire(**kwargs)
