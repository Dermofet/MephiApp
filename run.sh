#!/bin/bash

parse_date() {
  docker compose exec backend python /api/parsing/start_semester/parsing_date.py
}

parse_new_news() {
  docker compose exec backend python /api/parsing/news/run_parsing_new_news.py
}

parse_news() {
  docker compose exec backend python /api/parsing/news/run_parsing_news.py
  docker compose exec backend python /api/parsing/news/run_bulk_insert_news.py
}

parse_schedule() {
  docker compose exec backend python /api/parsing/schedule/run_parsing_schedule.py
  docker compose exec backend python /api/parsing/schedule/run_bulk_insert_schedule.py
}

build() {
  delete
  docker compose build
}

run() {
  docker compose up -d
}

stop() {
  docker compose stop
}

# shellcheck disable=SC2120
delete() {
  if [ -z "$2" ]; then
    if [ "$2" == "all" ]; then
      docker compose down -v
    else
      echo "Unexpected parameter"
    fi
  else
    docker compose down
  fi
}

create_migration() {
  if [ -z "$3" ]; then
    echo "Unexpected parameter"
    menu
    break
  fi

  docker compose exec backend alembic -c backend/alembic.ini revision --autogenerate -m "$3"
}

downgrade() {
  docker compose exec backend alembic -c backend/alembic.ini downgrade -1
}

upgrade() {
  docker compose exec backend alembic -c backend/alembic.ini upgrade head
}

alembic() {
  if [ -z "$2" ]; then
    echo "Unexpected parameter"
    menu
    break
  fi

  if [ "$2" = "create_migration" ]; then
    create_migration
  elif [ "$2" = "downgrade" ]; then
    downgrade
  elif [ "$2" = "upgrade" ]; then
    upgrade
  fi
}

menu() {
  echo "bash run.sh [command]"
  echo "commands:"
  echo "  build                     -  собрать проект и запустить его"
  echo "  run                       -  запустить сервер"
  echo "  stop                      -  остановить сервер"
  echo "  delete [all]              -  удалить контейнеры и текущий том. All - удалить все тома"
  echo "  parse_date                -  спарсить дату начала семестра и экспортировать в базу данных"
  echo "  parse_new_news            -  спарсить новые новости и экспортировать в базу данных"
  echo "  parse_news                -  спарсить все новости и экспортировать в базу данных"
  echo "  parse_schedule            -  спарсить расписание и экспортировать в базу данных"
  echo "  alembic [command]         -  работа с миграциями"
  echo "  - create_migration [msg]  -  создать миграцию для alembic. msg - комментарий миграции"
  echo "  - downgrade               -  откатить миграцию"
  echo "  - upgrade                 -  обновить миграцию"
}

command="$1"
if [ -z "$command" ]; then
  menu
  exit 0
else
  $command "$@"
fi