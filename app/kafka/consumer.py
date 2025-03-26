from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pathlib import Path
import logging
from datetime import datetime, timedelta, UTC
import time
from app.core.security import create_jwt_token
import asyncio

from app.kafka.schemas import EmailVerificationMessage

load_dotenv()

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    # Обновленные параметры:
    MAIL_STARTTLS=bool(os.getenv("MAIL_STARTTLS", True)),
    MAIL_SSL_TLS=bool(os.getenv("MAIL_SSL_TLS", False)),
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email"
)

class KafkaEmailConsumer:
    def __init__(self):
        self.kafka_servers = ['kafka:29092']
        self.topic = "email_verification"
        self.consumer = None
        self.running = False

    def _connect(self):
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.kafka_servers,
                    auto_offset_reset='earliest',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    enable_auto_commit=False
                )
                return
            except Exception as e:
                retry_count += 1
                print(f"Failed to connect to Kafka (attempt {retry_count}/{max_retries}): {e}")
                time.sleep(5)
        raise Exception(f"Failed to connect to Kafka after {max_retries} attempts")
    
    async def send_email(self, email: str, username: str, verify_email: str):
        verification_url = f"http://fastapi:8000/verify-email/{verify_email}"
        message = MessageSchema(
            subject="Подтверждение email",
            recipients=[email],
            template_body={
                "username": username,
                "verification_url": verification_url
            },
            subtype="html"
        )
        
        fm = FastMail(conf)
        try:
            await fm.send_message(message, template_name="verification.html")
            print(f"Verification email sent to {email}")
            return True
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")
            return False
    def process_message(self, message):
        """Обрабатывает сообщение из Kafka"""
        try:
            data = message.value
            email_message = EmailVerificationMessage(**data)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.send_email(
                    email_message.email, 
                    email_message.username, 
                    email_message.user_id,
                    email_message.verify_email,
                )
            )
            
            loop.close()
            
            if result:
                print(f"Successfully processed message for user {email_message.user_id}")
            else:
                print(f"Failed to process message for user {email_message.user_id}")
            
            return result
        except Exception as e:
            print(f"Error processing message: {e}")
            return False
    
    def start(self):
        """Запускает консьюмера для обработки сообщений"""
        self._connect()
        self.running = True
        
        print(f"Starting Kafka consumer for topic {self.topic}")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                success = self.process_message(message)
                
                if success:
                    self.consumer.commit()
        except Exception as e:
            print(f"Error in Kafka consumer: {e}")
        finally:
            self.close()
    
    def close(self):
        if self.consumer:
            self.consumer.close()
            print("Kafka consumer closed")
        self.running = False

kafka_consumer = KafkaEmailConsumer()
