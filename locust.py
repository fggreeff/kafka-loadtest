import os
import gevent
import json
import datetime

from uuid import uuid4
from locust import Locust, TaskSet, task, between
from kafka_producer import KafkaMessageProducer
from kafka_consumer import KafkaMessageConsumer


def start_consumer_thread(*args, **kwargs):
    consumer = KafkaMessageConsumer(
        HOST, out_topic_name, kwargs.get("state_map"))
    consumer.consume()


HOST = os.environ.get('KAFKA_HOST') or 'localhost:9092'
state_map = dict()
gevent.spawn(start_consumer_thread, state_map=state_map)

# This topic should exist in kafka
in_topic_name = 'raw.in'
out_topic_name = 'quote.stream.out'


class EventBehaviour(TaskSet):
    order_initiated_file_content = None
    order_completed_file_content = None
    date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    date_format_short = "%Y-%m-%d"

    def on_start(self):
        self.read_data()
        self.schedule_task(self.send_message)

    def read_data(self):
        self.order_initiated_file_content = open(
            "input/order_initiated.json").read()
        self.order_completed_file_content = open(
            "input/order_completed.json").read()

    @task
    def send_message(self):
        session_id = str(uuid4())
        datetime_now = datetime.datetime.now()

        order_initiated = json.loads(self.order_initiated_file_content)
        order_completed = json.loads(self.order_completed_file_content)

        order_initiated_str = self.update_initiated(
            order_initiated, session_id, datetime_now)
        order_completed_str = self.update_completed(
            order_completed, session_id, datetime_now)

        self.client.send(
            in_topic_name, message=order_initiated_str, key=session_id)
        self.client.send(
            in_topic_name, message=order_completed_str, key=session_id)

    def update_event(self, order, session_id, datetime_now):
        occurred_at = datetime_now + datetime.timedelta(0, 2)
        submitted_at = datetime_now + datetime.timedelta(0, 3)

        order["occurred_at"] = datetime_now.strftime(self.date_format_short)

        message_body = json.loads(order["message_body"])

        message_body["metadata"]["occurredAt"] = occurred_at.strftime(
            self.date_format)
        message_body["metadata"]["submittedAt"] = submitted_at.strftime(
            self.date_format)

        message_body["metadata"]["sessionId"] = session_id

        return message_body

    def update_completed(self, order, session_id, datetime_now):
        message_body = self.update_event(order, session_id, datetime_now)
        completed_at = datetime_now + datetime.timedelta(0, 4)

        message_body["metadata"]["completedAt"] = completed_at.strftime(
            self.date_format)

        order["message_body"] = str(json.dumps(message_body))

        return str(json.dumps(order))

    def update_initiated(self, order, session_id, datetime_now):
        message_body = self.update_event(order, session_id, datetime_now)

        order["message_body"] = str(json.dumps(message_body))

        return str(json.dumps(order))


class KafkaLocust(Locust):
    client = None

    def __init__(self, *args, **kwargs):
        super(KafkaLocust, self).__init__(*args, **kwargs)
        if not KafkaLocust.client:
            KafkaLocust.client = KafkaMessageProducer(HOST, state_map)


class ServiceUser(KafkaLocust):
    task_set = EventBehaviour
    wait_time = between(0.050, 0.100)
