#!/usr/bin/env bash
# {{ cookiecutter.app_name }} project start with gunicorn in produtcion environment

cd "$(dirname "$0")/.." || exit 0

gunicorn -c gunicorn.py "autoapp:app"
