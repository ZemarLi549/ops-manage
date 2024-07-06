from elasticsearch import Elasticsearch
from datetime import datetime,timedelta,date
import pymysql
import json
import decimal
import os
ES_HOSTS='http://172.30.14.379300'
ES_USERNAME = os.environ.get('ES_USERNAME', 'root')
ES_PWD = os.environ.get('ES_PWD', '123456')


class EsOperation:
    def __init__(self, es_host=ES_HOSTS, es_username=ES_USERNAME, es_password=ES_PWD):
        es_host_list = []
        for item in es_host.split(','):
            if not 'http' in item:
                es_host_list.append('http://' + item)
            else:
                es_host_list.append(item)
        self.es_username = es_username if es_username else ''
        self.es_password = es_password if es_password else ''
        self.es = Elasticsearch(es_host_list, basic_auth=(self.es_username, self.es_password), request_timeout=3600,verify_certs=False)

    def del_index(self):

        # 删除日期小于60天的索引
        index_name_prefix = 'opsalarm-'

        indices = self.es.indices.get_alias(index=index_name_prefix + '*')
        for index_name in indices:
            index_date_str = index_name.split('-')[-1]
            index_date = datetime.strptime(index_date_str, '%Y.%m.%d')
            if index_date < DATE_CUTOFF:
                self.es.indices.delete(index=index_name)
                print(f"Deleted index: {index_name}")


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj, datetime.datetime):
        #     return int(mktime(obj.timetuple()))
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)

class MysqlOp():
    def __init__(self):
        self.MYSQL_HOST = '172.30.14.39'
        self.MYSQL_PORT = 3306
        self.MYSQL_USER = 'root'
        self.MYSQL_PWD = '123456'

        self.MYSQL_DB = 'ops_manage'
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
                               port=self.MYSQL_PORT,
                               user=self.MYSQL_USER,
                               passwd=self.MYSQL_PWD,
                               db=self.MYSQL_DB,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        return conn, cur


    def mysql_other_op(self, sql_sentence):
        print(sql_sentence)
        try:
            self.cur.execute(sql_sentence)
            self.conn.commit()
            insert_id = self.cur.lastrowid
            print('成功执行语句')
        except Exception as e:
            insert_id = 0
            self.conn.rollback()
            print(e)
            print('失败！！！')
        return insert_id

    # 关闭游标和数据库的连接
    def __del__(self):
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':

    NOW_TIME = datetime.now()
    DELTA_TIME = 120
    DATE_CUTOFF = NOW_TIME - timedelta(days=DELTA_TIME)
    DATE_CUTOFF_STR = DATE_CUTOFF.strftime('%Y-%m-%d %H:%M:%S')
    print(f'>>>del 小于{DATE_CUTOFF_STR}的数据')
    es_op = EsOperation()
    es_op.del_index()
    mysqlOp = MysqlOp()

    set_check_off = 'SET FOREIGN_KEY_CHECKS = 0;'
    mysqlOp.mysql_other_op(set_check_off)


    delete_str = f'''DELETE alarm_comment,alarm_zongjie
FROM alarm_identity
LEFT JOIN alarm_comment ON alarm_comment.identity_id = alarm_identity.id
LEFT JOIN alarm_zongjie ON alarm_zongjie.identity_id = alarm_identity.id
WHERE alarm_identity.updated_at < '{DATE_CUTOFF}' and alarm_identity.status=0;'''
    mysqlOp.mysql_other_op(delete_str)

    delete_str = f'''DELETE FROM alarm_identity WHERE updated_at < '{DATE_CUTOFF}' and alarm_identity.status=0;'''
    mysqlOp.mysql_other_op(delete_str)

    set_check_on = 'SET FOREIGN_KEY_CHECKS = 0;'
    mysqlOp.mysql_other_op(set_check_on)

