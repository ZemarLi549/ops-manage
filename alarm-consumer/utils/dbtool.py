from ops_alarm import settings
import pymysql
import json
import simplejson
import decimal
import datetime
import binascii
from utils.logger import logger
import logging
logger = logging.getLogger(__name__)
from functools import wraps
import uuid
def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return get_instance
class MyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            result = float(obj)
        elif isinstance(obj, (datetime.timedelta, uuid.UUID)):
            result = str(obj)
        elif isinstance(obj, datetime.time):
            if obj.utcoffset() is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            result = obj.isoformat()
            if obj.microsecond:
                result = result[:12]
        elif isinstance(obj, memoryview):
            result = binascii.hexlify(obj).decode()
        elif isinstance(obj, bytes):
            result = binascii.hexlify(obj).decode()
        else:
            return json.JSONEncoder.default(self, obj)
# @singleton
class MysqlOp():
    def __init__(self):
        # self.MYSQL_HOST = '172.30.14.39'
        # self.MYSQL_PORT = '3306'
        # self.MYSQL_USER = 'root'
        # self.MYSQL_PWD = '123456'
        # self.MYSQL_DB ='ops_manage'
        self.MYSQL_HOST = settings.MYSQL_DB_HOST
        self.MYSQL_PORT = settings.MYSQL_DB_PORT
        self.MYSQL_USER = settings.MYSQL_DB_USER
        self.MYSQL_PWD = settings.MYSQL_DB_PASSWD
        self.MYSQL_DB = settings.MYSQL_DB_NAME
        self.conn, self.cur = self.connect_mysql()

    @staticmethod
    def _escape_regexp_special(patten):
        special_char = ['\\', '$', '*', '[', ']', '(', ')', '+', '.', '?', '{', '}', '^', '|']
        for char in special_char:
            if patten.find(char) > 0:
                patten = patten.replace(char, '\\\\' + char)
        return patten

    def connect_mysql(self):
        conn = pymysql.connect(host=self.MYSQL_HOST,
                               port=int(self.MYSQL_PORT),
                               user=self.MYSQL_USER,
                               passwd=self.MYSQL_PWD,
                               db=self.MYSQL_DB,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        return conn, cur

    def insert_info(self, table_name, data):  # keyc重复更新
        """
        data={'id':10001,'emp_name':'lzx}
        :param data:
        :return:
        """

        k = ','.join(data.keys())
        v = ('%s,' * len(data))[:-1]
        sql = "INSERT INTO {t} ({k}) values ({v}) ON DUPLICATE KEY UPDATE ".format(t=table_name, k=k, v=v)
        update = ','.join(["{} = %s".format(key) for key in data.keys()])
        sql += update
        logger.info(sql)
        insert_id = 0
        try:
            self.cur.execute(sql, tuple(data.values()) * 2)
            self.conn.commit()
            insert_id = self.cur.lastrowid
        except Exception as e:
            logger.error(f'失败:{e}')
            self.conn.rollback()
            pass
        return insert_id

    def insertorupdate(self, table_name, condition, u_condition, insert_data, update_data):  # condition重复更新
        """
        data={'id':10001,'emp_name':'lzx}
        :param data:
        :return:
        """
        u_k = ','.join(["{} = %s".format(key) for key in update_data.keys()])
        i_k = ','.join(insert_data.keys())
        i_v = ('%s,' * len(insert_data))[:-1]
        sql = "IF EXISTS (SELECT 1 FROM {t} WHERE {condition}) UPDATE {t} SET {u_k} WHERE {u_condition} ELSE INSERT INTO {t} ({i_k}) values ({i_v})".format(
            t=table_name, condition=condition, u_k=u_k, u_condition=u_condition, i_k=i_k, i_v=i_v)

        try:
            self.cur.execute(sql, tuple(update_data.values() + insert_data.values()))
            self.conn.commit()
        except Exception as e:
            logger.info(e)
            self.conn.rollback()
            logger.info('失败')
            logger.info(sql)
            pass
        pass

    def jsonfy(self, result_ls):
        if result_ls:
            # after_set=result_ls
            after_set = json.dumps(result_ls, ensure_ascii=False, cls=MyEncoder)
            after_set = json.loads(after_set)
        else:
            after_set = []
        return after_set
    def mysql_dict_query(self, sql_sentence,*args):
        logger.info(sql_sentence)
        self.cur.execute(sql_sentence,*args)
        result_ls = self.cur.fetchall()
        userinfo = self.jsonfy(result_ls)

        return userinfo

    def curl_op(self, sql_sentence, *args):
        logger.info(sql_sentence)
        self.cur.execute(sql_sentence, *args)
        result_ls = self.cur.fetchall()
        userinfo = self.jsonfy(result_ls)
        return self.cur.description, userinfo

    def mysql_find_op(self, sql_sentence):
        logger.info(sql_sentence)
        self.cur.execute(sql_sentence)
        result_ls = self.cur.fetchall()
        userinfo = self.jsonfy(result_ls)

        return userinfo
    def update_info(self, table_name, data,condition):
        kv_str  = ''
        for key,val in data.items():
            kv_str+=f"`{key}`='{val}',"
        kv_str = kv_str.strip(',')
        sql = f"UPDATE `{table_name}` SET {kv_str} {condition}"
        # logger.info(sql)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            self.conn.rollback()
            logger.error('失败')
            pass
        pass
    def mysql_other_op(self, sql_sentence):
        logger.info(sql_sentence)
        try:
            self.cur.execute(sql_sentence)
            self.conn.commit()
            insert_id = self.cur.lastrowid
            logger.info('成功执行语句')
        except Exception as e:
            insert_id = 0
            self.conn.rollback()
            logger.info(e)
            logger.info('失败！！！')

        return insert_id

    # 关闭游标和数据库的连接
    def __del__(self):
        self.cur.close()
        self.conn.close()
# import time
# insert_data = {
#                 "identity":'dsfdsfds',
#                 "identity_tag_kv":json.dumps({'id':3303,'instance':'10.110.1.17'}),
#                 "times":1,
#                 "score":5,
#                 "status":4,
#                 "created_at":time.strftime('%Y-%m-%d %H:%M:%S'),
#                 "updated_at":time.strftime('%Y-%m-%d %H:%M:%S'),
#                 "created_by":'sys',
#                 "updated_by":'sys',
#                 "record_ignore":1,
#             }
# resp = MysqlOp().insert_info('alarm_identity',insert_data)
# print(resp,type(resp))