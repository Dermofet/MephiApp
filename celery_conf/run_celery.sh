#!/bin/bash
# python celery_conf/install_lang_packages.py
celery --app celery_conf.beat.beat_app beat --loglevel=info & celery --app celery_conf.beat.beat_app worker --loglevel=info -P eventlet & tail -f /dev/null