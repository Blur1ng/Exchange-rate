from kafka import KafkaProducer
import json
import logging
from app.kafka.schemas import EmailVerificationMessage

import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class KafkaEmailProducer:
    def __init__(self):
        self.kafka_servers = [os.getenv("KAFKA_BOOTSTRAP_SERVERS")]
        self.topic = "email_verification"
        self.producer = None

    def connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['kafka:29092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None
            )
            print(f"Connected to Kafka at {self.kafka_servers}")
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")
            raise

    def send_verification_email(self, email: str, username: str, user_id: int, verify_email: str):
        message = EmailVerificationMessage(
            email=email,
            username=username,
            user_id=user_id,
            verify_email=verify_email
        )

        try:
            future = self.producer.send(
                topic=self.topic,
                value=message.model_dump(),
                key=user_id,
            )

            data = future.get(timeout=10)
            print(f"Message sent to topic {data.topic}, partition {data.partition}, offset {data.offset}")
            return True
        except Exception as e:
            print(f"Failed to send message to Kafka: {e}")
            return False
    def close(self):
        if self.producer:
            self.producer.close()

kafka_producer = KafkaEmailProducer()

            


