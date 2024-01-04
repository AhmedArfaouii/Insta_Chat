import pika
from ldapserver import hash_password

class RabbitMQAuth:
    def __init__(self, login, password):
        self.credentials = pika.PlainCredentials(login, hash_password(password))
        self.connection = None
        self.channel = None
        self.logged_in = False

    def connect_to_rabbitmq(self):
        parameters = pika.ConnectionParameters('localhost', credentials=self.credentials)
        try:
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.logged_in = True
        except pika.exceptions.AMQPConnectionError:
            self.logged_in = False

    def authenticate(self):
        return self.logged_in
