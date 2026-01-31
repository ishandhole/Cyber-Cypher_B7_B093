import json
import logging
from typing import Callable, Any, Dict
import queue
import threading
import time

logger = logging.getLogger("kafka_mock")

# Mock Kafka for standalone execution without docker-compose dependencies running
class MockKafkaProducer:
    def __init__(self, topic: str):
        self.topic = topic
    
    def send(self, message: Dict[str, Any]):
        logger.info(f"MOCK PRODUCER [{self.topic}]: {json.dumps(message)}")
        # In a real mock, we might push to a shared queue if we had consumers in the same process
        pass
    
    def close(self):
        pass

class MockKafkaConsumer:
    def __init__(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        self.topic = topic
        self.callback = callback
        self.running = False
        self.thread = None
        self._queue = queue.Queue()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._consume_loop)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _consume_loop(self):
        while self.running:
            try:
                msg = self._queue.get(timeout=1.0)
                self.callback(msg)
            except queue.Empty:
                continue

    # Method to simulate receiving a message from external source
    def inject_message(self, message: Dict[str, Any]):
        self._queue.put(message)

# Interface to switch between Real and Mock
class EventBus:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.producers = {}
        self.consumers = []

    def get_producer(self, topic: str):
        if self.use_mock:
            if topic not in self.producers:
                self.producers[topic] = MockKafkaProducer(topic)
            return self.producers[topic]
        else:
            # Placeholder for real KafkaProducer
            from kafka import KafkaProducer
            return KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def start_consumer(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        if self.use_mock:
            consumer = MockKafkaConsumer(topic, callback)
            consumer.start()
            self.consumers.append(consumer)
            return consumer
        else:
            # Placeholder for real KafkaConsumer logic
            pass
