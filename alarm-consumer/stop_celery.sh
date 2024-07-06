#!/bin/bash
ps -ef|egrep 'celery'|grep -v grep|awk '{print $2}'|xargs kill -9