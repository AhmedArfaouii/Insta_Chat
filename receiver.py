import pika
from test import hash_password

def connexion ():  
            # Define RabbitMQ connection parameters with credentials
        login = input ("Enter your login : ")
        intial_password = input ("Enter your password : ")
        password = hash_password (intial_password)
        credentials = pika.PlainCredentials(login, password)
        parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)

        # Establish a connection to RabbitMQ
        connection = pika.BlockingConnection(parameters)
        print("Connection to RabbitMQ established successfully: All good!")

        return connection

def callback(ch, method, properties, body):
    print("Received:", body.decode())

connection = connexion()
channel = connection.channel()
channel.basic_consume(queue='chat', on_message_callback=callback, auto_ack=True)

print('Waiting for messages...')
channel.start_consuming()