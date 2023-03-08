from celery import Celery

from . import config

# Celery
print(config.celery_broker_url)
celery = Celery('celery', broker=config.celery_broker_url)
celery.logger = get_task_logger(__name__)

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='academic_create', durable=True)
channel.queue_declare(queue='corps_create', durable=True)
channel.queue_declare(queue='group_create', durable=True)
channel.queue_declare(queue='room_create', durable=True)
channel.queue_declare(queue='teacher_create', durable=True)
channel.queue_declare(queue='lesson_create', durable=True)
channel.queue_declare(queue='teacher_update', durable=True)
