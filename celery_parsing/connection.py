import pika
from celery import Celery

from celery_parsing import myconfig

# Celery
celery = Celery('celery', broker=myconfig.CELERY_BROKER_URL)

# Подключение к RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672, virtual_host='/'))
except (Exception, ):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, virtual_host='/'))
    except (Exception, ):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1', port=5672, virtual_host='/'))
channel = connection.channel()
channel.queue_declare(queue='academic_create', durable=True)
channel.queue_declare(queue='corps_create', durable=True)
channel.queue_declare(queue='group_create', durable=True)
channel.queue_declare(queue='room_create', durable=True)
channel.queue_declare(queue='teacher_create', durable=True)
channel.queue_declare(queue='lesson_create', durable=True)
channel.queue_declare(queue='teacher_update', durable=True)
