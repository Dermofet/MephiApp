#!/bin/bash

init() {
  source /venv/bin/activate
  export PYTHONPATH=$PYTHONPATH:$(realpath "$(dirname "$0")")
}

parse() {
  script_dir="$(dirname "$0")"
  docker compose exec celery python "$script_dir/etl/etl_.py" "$2"
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
    docker compose down
    return
  fi

  if [ "$2" = "all" ]; then
    docker compose down -v
    return
  fi

  echo "Unexpected parameter"
}

create_migration() {
  docker compose exec backend alembic -c backend/alembic.ini revision --autogenerate -m "$1"
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
    return
  fi

  if [ "$2" = "create_migration" ]; then
    if [ -z "$3" ]; then
      echo "Unexpected parameter"
      menu
      return
    fi
    create_migration "$3"
  elif [ "$2" = "downgrade" ]; then
    downgrade
  elif [ "$2" = "upgrade" ]; then
    upgrade
  fi
}

menu() {
  echo "bash run.sh [command]"
  echo "commands:"
  echo "  init                          -  настройка окружения"
  echo "  build                         -  собрать проект и запустить его"
  echo "  run                           -  запустить сервер"
  echo "  stop                          -  остановить сервер"
  echo "  delete [all]                  -  удалить контейнеры и текущий том. All - удалить все тома"
  echo "  parse [command]               -  работа с парсерами"
  echo "  - start_semester              -  спарсить дату начала семестра и экспортировать в базу данных"
  echo "  - all_news                    -  спарсить новости и экспортировать в базу данных"
  echo "  - new_news                    -  спарсить новые новости и экспортировать в базу данных"
  echo "  - schedule                    -  спарсить расписание и экспортировать в базу данных"
  echo "  alembic [command]             -  работа с миграциями"
  echo "  - create_migration [msg]      -  создать миграцию для alembic. msg - комментарий миграции"
  echo "  - downgrade                   -  откатить миграцию"
  echo "  - upgrade                     -  обновить миграцию"
}

command="$1"
if [ -z "$command" ]; then
  menu
  return 0
else
  $command "$@"
fi