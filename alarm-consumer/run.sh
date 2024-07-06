#!/bin/bash
if [[ -v RUN_FLOWER && $RUN_FLOWER == "1" ]]; then
    celery -A celery_tasks flower --address=0.0.0.0 --port=5555
else
    celery -A celery_tasks worker -l info -Q ${OPS_TASK_NAME:-ops_alarm_consumer} -c 15
fi
# python -m celery -A celery_tasks flower --address=0.0.0.0 --port=5555
# celery -A celery_tasks worker -l info -Q ${OPS_TASK_NAME:-ops_alarm_consumer},${OPS_SAVE_NAME:-ops_alarm_saver} -c 10
