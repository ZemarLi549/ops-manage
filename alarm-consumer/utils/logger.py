
import logging
import os
import sys
from ops_alarm.settings import LOG_LEVEL,LOG_STDOUT
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)


def init_logger(log_path, name):
    True if os.path.exists(log_path) else os.makedirs(log_path)
    handler = logging.StreamHandler(sys.stdout if LOG_STDOUT else sys.stderr)
    # fmt = '[%(asctime)s][%(levelname)s][%(filename)s][%(funcName)s][%(lineno)s] %(message)s'
    fmt = '[%(asctime)s.%(msecs)03d] [%(filename)s:%(lineno)d] [%(levelname)s] - [%(message)s]"'
    file_handler = RotatingFileHandler(f"{log_path}/{name}.log", maxBytes=50 * 1024 * 1024, backupCount=5,encoding='utf-8')
    formatter = logging.Formatter(fmt)
    file_handler.setFormatter(formatter)
    handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)