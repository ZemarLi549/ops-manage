from ops_alarm import settings
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime
import pickle

def make_token():
    data = str(datetime.now())
    hash_str=hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
    return hash_str

def parse_boolean(s):
    """Takes a string and returns the equivalent as a boolean value."""
    s = s.strip().lower()
    if s in ("yes", "true", "on", "1"):
        return True
    elif s in ("no", "false", "off", "0", "none"):
        return False
    else:
        raise ValueError("Invalid boolean value %r" % s)


def encrypt(body, key=settings.ENCRYPT_KEY):
    f = Fernet(bytes(key.encode("utf8")))
    bytejson = pickle.dumps(body)
    encrypt_string = f.encrypt(bytejson)
    return encrypt_string


def decrypt(encrypt_string, key=settings.ENCRYPT_KEY):
    f = Fernet(bytes(key.encode("utf8")))
    strings = f.decrypt(encrypt_string)
    body = pickle.loads(strings)
    return body