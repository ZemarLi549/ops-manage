import os
from dotenv import load_dotenv

def parse_boolean(s):
    """Takes a string and returns the equivalent as a boolean value."""
    s = s.strip().lower()
    if s in ("yes", "true", "on", "1"):
        return True
    elif s in ("no", "false", "off", "0", "none"):
        return False
    else:
        raise ValueError("Invalid boolean value %r" % s)
load_dotenv(verbose=True)
MYSQL_DB_NAME = os.environ.get('MYSQL_DB_NAME', 'ops_manage')
MYSQL_DB_USER = os.environ.get('MYSQL_DB_USER', 'root')
MYSQL_DB_PASSWD = os.environ.get('MYSQL_DB_PASSWD', '123456')
MYSQL_DB_HOST = os.environ.get('MYSQL_DB_HOST', '172.30.14.37')
MYSQL_DB_PORT = os.environ.get('MYSQL_DB_PORT', '3307')
MYSQL_DB_LOG_TABLE = os.environ.get('MYSQL_DB_LOG_TABLE', 's_tasklog')


REDIS_URL = os.environ.get('REDIS_URL', 'redis://:123456@172.30.14.37:6380/1')
REDIS_HOST=os.environ.get('REDIS_HOST','172.30.14.37')
REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD','123456')
REDIS_PORT=os.environ.get('REDIS_PORT',6380)
REDIS_DB=os.environ.get('REDIS_DB',5)
IS_REDIS_CLUSTER=os.environ.get('IS_REDIS_CLUSTER','0')
REDIS_BACK_DB=os.environ.get('REDIS_BACK_DB',11)
if IS_REDIS_CLUSTER == '1':
    REDIS_DB = 0
    REDIS_BACK_DB = 0
LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO")

BASE_LOG_PATH=os.environ.get("BASE_LOG_PATH", "/data/logs")
SERVICE_NAME=os.environ.get("SERVICE_NAME", "alarm-consumer")
LOG_PATH=f"{BASE_LOG_PATH}/{SERVICE_NAME}"
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
LOG_STDOUT = parse_boolean(os.environ.get("LOG_STDOUT", "true"))
ENCRYPT_KEY = os.environ.get("ENCRYPT_KEY", "noUjOmvz5zgot45GzQcdFj3258bQs-743hL8HuWEadc=")
C_FORCE_ROOT = os.environ.setdefault('C_FORCE_ROOT','True')
RESOLVED_TIME = os.environ.setdefault('RESOLVED_TIME','600')
OPSMANAGE_DOMAIN = os.environ.setdefault('OPSMANAGE_DOMAIN','http://172.30.14.37:4346')


MAIL_HOST = os.environ.get("MAIL_HOST", "xxx:465")
MAIL_USER = os.environ.get("MAIL_USER", "xxx@xxx.com")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "xxx")

SMS_URL = os.environ.get("SMS_URL", "http://dcsms.xxx")
SMS_PASS = os.environ.get("SMS_PASS", "24a62954-xxx")

ES_HOSTS = os.environ.get("ES_HOSTS", "https://172.30.14.39:9200")
ES_USERNAME = os.environ.get("ES_USERNAME", "elastic")
ES_PWD = os.environ.get("ES_PWD", "123456")