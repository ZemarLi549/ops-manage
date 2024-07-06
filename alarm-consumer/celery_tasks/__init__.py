import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from utils.logger import init_logger
from ops_alarm.settings import LOG_PATH,SERVICE_NAME
init_logger(LOG_PATH,SERVICE_NAME)
print('run once>>>>')