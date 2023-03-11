import time

import pika
from celery import Celery

from celery_parsing import myconfig
from celery_parsing.worker import Worker

# Celery
celery = Celery('celery', broker=myconfig.CELERY_BROKER_URL)

# Подключение к RabbitMQ
# while True:
#     try:
#
#     except (Exception,) as err:
#         print(f'rabbitmq connection failed; error: {err}\n'
#               f'retrying in 1 second...')
#         time.sleep(1)
#     else:
#         break
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='Worker.academic_create', durable=True)
channel.queue_declare(queue='Worker.corps_create', durable=True)
channel.queue_declare(queue='Worker.group_create', durable=True)
channel.queue_declare(queue='Worker.room_create', durable=True)
channel.queue_declare(queue='Worker.teacher_create', durable=True)
channel.queue_declare(queue='Worker.lesson_create', durable=True)
channel.queue_declare(queue='Worker.teacher_update', durable=True)
