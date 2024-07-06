import jwt
import time
from django.conf import settings
def generate_jwt(payload, expiry, secret=None):
    """
    生成jwt
    :param payload: dict 载荷
    :param expiry: datetime 有效期
    :param secret: 密钥
    :return: jwt
    """

    _payload = {'exp': int(time.time()) + expiry}
    _payload.update(payload)


    if not secret:
        secret = settings.SECRET_KEY

    token = jwt.encode(_payload, secret, algorithm='HS256')
    return token


def verify_jwt(token, secret=None):
    """
    检验jwt
    :param token: jwt
    :param secret: 密钥
    :return: dict: payload
    """
    if not secret:
        secret = settings.SECRET_KEY

    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return True, payload
    except Exception as e:
        return False, e