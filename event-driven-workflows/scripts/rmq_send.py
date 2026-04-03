import pika

# Replace with your RabbitMQ service DNS or 'localhost' if port-forwarding
credentials = pika.PlainCredentials('${RMQ_USER}', '${RMQ_PASS}')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='${RMQ_IP}', credentials=credentials))
channel = connection.channel()

# Declare the queue (creates it if it doesn't exist)
channel.queue_declare(queue='hello')

# Send the message
channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
print(" [x] Sent 'Hello World!'")

connection.close()
