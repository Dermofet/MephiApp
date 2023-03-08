from celery import Celery

from celery_parsing import config

# Celery
print(config.CELERY_BROKER_URL)
celery = Celery('celery', broker=config.celery_broker_url)

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
