#!/usr/bin/env bash
# celery worker, beat, flower start script

cd "$(dirname "$0")/.." || exit 0

PROJECT_NAME="${PROJECT_NAME:-{{cookiecutter.app_name}}}"

name="${1}"


LOG_DIR="${HOME}/logs/${PROJECT_NAME}"

case "${name}" in
worker|-w|-W)
    # celery  multi start -A "${PROJECT_NAME}.tasks.celery_app:app" worker -fair \
    test -e "${LOG_DIR}/celery-worker.pid" && rm -f "${LOG_DIR}/celery-worker.pid"
    celery \
        -A "${PROJECT_NAME}.tasks.celery_app:app" worker \
        -fair \
        -E \
        -l INFO  \
        --logfile="${LOG_DIR}/worker.log" \
        --pidfile="${LOG_DIR}/celery-worker.pid"
        # -D # --detach      Start worker as a background process.
        # -n, --hostname HOSTNAME         Set custom hostname (e.g., 'w1@%%h').
    ;;
beat|-b|-B)
    test -e "${LOG_DIR}/celery-beat.pid" && rm -f "${LOG_DIR}/celery-beat.pid"
    celery \
        -A "${PROJECT_NAME}.tasks.celery_app:app" beat \
        -l INFO \
        --pidfile "${LOG_DIR}/celery-beat.pid" \
        -s "${LOG_DIR}/celerybeat-schedule" \
        --logfile="${LOG_DIR}/beat.log"
        # --detach    Detach and run in the background as a daemon.
    ;;

flower|-web)
    celery  -A "${PROJECT_NAME}.tasks.celery_app:app" flower
    ;;
*)
    echo "usage:"
    echo "worker|-w|-W : start worker"
    echo "celery.sh worker"
    echo "beat|-b|-B : start beat"
    echo "celery.sh beat"
    echo "flower|-web : start celery web"
    echo "celery flower"
esac
