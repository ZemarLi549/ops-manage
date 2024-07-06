#coding=utf-8
import os
import traceback
import importlib
import requests
from requests import HTTPError
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
def convert_to_relative_time(time_str):
    # 获取当前时间
    current_time = datetime.now()

    # 将时间字符串转换为datetime对象
    time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    # 计算时间差
    time_difference = current_time - time

    # 分别计算相差的天数、小时数和分钟数
    days = time_difference.days
    hours = time_difference.seconds // 3600
    minutes = (time_difference.seconds // 60) % 60

    # 根据时间差生成相对时间字符串
    if days > 0:
        return f"{days}天前"
    elif hours > 0:
        return f"{hours}小时前"
    elif minutes > 0:
        return f"{minutes}分钟前"
    else:
        return "刚刚"
def do_request(url, method, headers={}, params=None, data=None, json=None):
    try:
        res = requests.request(method.upper(), url, params=params, data=data, json=json,
            headers=headers, timeout=(60.0, 60.0), verify=False)
        # logger.warning('Method: %s, Url: %s', method.upper(), url)
        if res.status_code == 204:
            return {'error': 0, 'code': None, 'msg': 'ok 204'}
        res_json = res.json()
        # logger.info('res json: %s', str(res_json))
        return res_json
    except HTTPError as ex:
        status_code = ex.response.status_code
        logger.error('HTTPError (%d): %s', status_code,
            ex.response.content.decode('utf-8'))
        try:
            return {
                'error': status_code,
                'code': None,
                'msg': res.text()
            }
        except Exception:
            return {
                'error': status_code,
                'code': None,
                'msg': 'HTTPError ({})'.format(ex.response.content.decode('utf-8'))
            }
    except Exception as exc:
        logger.error('do_request error: %s\n%s', str(exc), traceback.format_exc())
        return {
            'error': 1,
            'code': None,
            'msg': 'ApplicationError ({})'.format(exc)
        }
class Execution(object):
    def __init__(self, logger=None):
        self.models = None
    def load_plugins(self,app_name,file_name,keywords):
        """
        加载模块
        @param name string:插件相对models的命名空间
        @return dict:
        """
        funcs = {}
        module_path = '.'.join(['apps',app_name,file_name])
        schema_module = importlib.import_module(module_path)
        module = dir(schema_module)
        for attr in module:
            if keywords in attr and attr != keywords:
                if attr.startswith('_'):
                    continue
                    #将加载的模块存放到字典里面
                func = getattr(schema_module, attr)
                if isinstance(func,object):
                    try:
                        funcs[attr] = func
                    except:
                        print(traceback.format_exc())
                else:
                    continue
        return funcs


import pickle
from cryptography.fernet import Fernet
def encrypt(body, key):
    f = Fernet(bytes(key.encode("utf8")))
    bytejson = pickle.dumps(body)
    encrypt_string = f.encrypt(bytejson)
    msg = encrypt_string.decode('utf-8')
    return msg

def decrypt(encrypt_string, key):
    word = bytes(encrypt_string.encode("utf-8"))

    f = Fernet(bytes(key.encode("utf8")))
    strings = f.decrypt(word)
    body = pickle.loads(strings)
    return body



