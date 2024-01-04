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
                print(f"Received and decrypted message: {decrypted_message}")
                self.channel.basic_ack(method_frame.delivery_tag)
            else:
                print("No message in the queue")
        except Exception as e:
            print(f"Decryption failed: {e}")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Connection closed")


recipient_login = input("Enter your login to receive your messages: ") # Replace with the recipient's login name
recipient_password = input("Enter your password: ")  # Replace with the recipient's password for RabbitMQ

receiver = MessageReceiver(recipient_login, recipient_password)
receiver.connect_to_rabbitmq()
private_key = receiver.load_private_key_from_file("python_test_private.pem")  # Replace with the path to recipient's private key file
queue_name = "queue"  # Replace with the queue name where messages are sent

receiver.receive_and_decrypt_message(queue_name, private_key)

receiver.close_connection()
