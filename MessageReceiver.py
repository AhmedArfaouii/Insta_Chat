from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import pika

from ldapserver import hash_password

class MessageReceiver:
    def __init__(self, login, password):
        self.credentials = pika.PlainCredentials(login, hash_password(password))
        self.connection = None
        self.channel = None

    def connect_to_rabbitmq(self):
        parameters = pika.ConnectionParameters('localhost', credentials=self.credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def load_private_key_from_file(self, filename):
        with open(filename, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
        return private_key

    def receive_and_decrypt_message(self, queue_name, private_key):
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue_name)
            if method_frame:
                decrypted_message = private_key.decrypt(
                    body,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()
                self.channel.basic_ack(method_frame.delivery_tag)
                return decrypted_message
            else:
                return None
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()


