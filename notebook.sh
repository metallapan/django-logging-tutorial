#!/bin/sh
.venv/bin/pip install -r requirements.extra.txt
DJANGO_ALLOW_ASYNC_UNSAFE=true .venv/bin/python manage.py shell_plus --lab
