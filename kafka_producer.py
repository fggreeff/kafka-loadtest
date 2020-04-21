import time

from kafka import KafkaProducer
from locust import events


class KafkaMessageProducer:

    def __init__(self, kafka_brokers=None, state_map=None):

        if kafka_brokers is None:
            kafka_brokers = ['localhost:9092']
        self.producer = KafkaProducer(bootstrap_servers=kafka_brokers)
        self.state_map = state_map

    def __handle_success(self, *arguments, **kwargs):
        produced_at_time_millis = time.time()*1000

        self.state_map[kwargs.get("key")] = produced_at_time_millis

    def __handle_failure(self, *arguments, **kwargs):
        end_time = time.time()
        elapsed_time = int((end_time - kwargs["start_time"]) * 1000)

        request_data = dict(request_type="ENQUEUE", name=kwargs["topic"], response_time=elapsed_time,
                            exception=arguments[0])

        self.__fire_failure(**request_data)

    def __fire_failure(self, **kwargs):
        events.request_failure.fire(**kwargs)

    def __fire_success(self, **kwargs):
        events.request_success.fire(**kwargs)

    def send(self, topic, key=None, message=None):

        start_time = time.time()
        future = self.producer.send(topic, key=key.encode() if key else None,
                                    value=message.encode() if message else None)

        future.add_callback(self.__handle_success,
                            start_time=start_time, future=future, key=key)
        future.add_errback(self.__handle_failure,
                           start_time=start_time, topic=topic)

    def finalize(self):
        self.producer.flush(timeout=5)
