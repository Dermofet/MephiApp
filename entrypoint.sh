#!/bin/bash

echo "$ENV"

if [ "$ENV" == "development" ]; then
  alembic upgrade head
fi

chmod +x run_bulk_insert_news.sh run_bulk_insert_schedule.sh run_parsing_news.sh run_parsing_schedule.sh run_parsing_date.sh run_parsing_new_news.sh

python runserver.py