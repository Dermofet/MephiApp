#!/bin/bash

echo "$ENV"

if [ "$ENV" == "development" ]; then
  alembic -c backend/alembic.ini upgrade head
fi

python backend/runserver.py