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

def send_to_rabbitmq(message):
    try:
        connection = connexion()
        channel = connection.channel()

        channel.queue_declare(queue='chat')
        channel.basic_publish(exchange='', routing_key='chat', body=message)
        print("Sent:", message)
        connection.close()
        
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")



# send_message("Hello, how are you RECEIVER?")