from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import pika
from ldapserver import hash_password

class RabbitMQManager:
    def __init__(self, login, password):
        self.credentials = pika.PlainCredentials(login, hash_password(password))
        self.connection = None
        self.channel = None

    def connect_to_rabbitmq(self):
        parameters = pika.ConnectionParameters('localhost', credentials=self.credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def generate_keys(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        return private_key, public_key

    def save_private_key_to_file(self, private_key, filename):
        with open(filename, "wb") as key_file:
            key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

    def save_public_key_to_file(self, public_key, filename):
        with open(filename, "wb") as key_file:
            key_file.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

    def load_public_key_from_file(self, filename):
        with open(filename, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
        return public_key
    
    def encrypt_message(self, message, public_key):
        cipher_text = public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return cipher_text
    def send_encrypted_message(self, recipient, encrypted_message, queue_name):
        self.channel.queue_declare(queue=queue_name)  # Declare the queue
        self.channel.basic_publish(exchange='', routing_key=queue_name, body=encrypted_message)
        print(f"Sent encrypted message to {recipient} in queue: {queue_name}")


    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Connection closed")

# Example usage to send a message from one user to another
sender_login = input("Enter your login: ")
sender_password = input("Enter your password: ")

sender_manager = RabbitMQManager(sender_login, sender_password)
sender_manager.connect_to_rabbitmq()

recipient_login = input("Enter recipient's login: ")
message_to_recipient = input("Enter message: ")

# Generate keys for sender and recipient
sender_private_key, sender_public_key = sender_manager.generate_keys()
sender_manager.save_private_key_to_file(sender_private_key, f"{sender_login}_private.pem")
sender_manager.save_public_key_to_file(sender_public_key, f"{sender_login}_public.pem")

recipient_private_key, recipient_public_key = sender_manager.generate_keys()
sender_manager.save_private_key_to_file(recipient_private_key, f"{recipient_login}_private.pem")
sender_manager.save_public_key_to_file(recipient_public_key, f"{recipient_login}_public.pem")

recipient_public_key = sender_manager.load_public_key_from_file(f"{recipient_login}_public.pem")
encrypted_message = sender_manager.encrypt_message(message_to_recipient, recipient_public_key)
queue_name = "queue"
sender_manager.send_encrypted_message(recipient_login, encrypted_message, queue_name)

sender_manager.close_connection()
