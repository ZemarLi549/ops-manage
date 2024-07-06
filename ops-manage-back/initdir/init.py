
import re

import os
from datetime import datetime

import MySQLdb
MYSQL_DB_HOST = '127.0.0.1'
MYSQL_DB_NAME = 'ops_manage'
MYSQL_DB_USER = 'root'
MYSQL_DB_PASSWD = 'piecelovewudi'
def connect_mysql():
    db = MySQLdb.connect(host=MYSQL_DB_HOST, port=3307, db=MYSQL_DB_NAME,
                         user=MYSQL_DB_USER,
                         password=MYSQL_DB_PASSWD,charset='utf8')
    cursor = db.cursor()
    return db, cursor
def insert_info(table_name,data):#keyc重复更新
    """
    data={'id':10001,'emp_name':'lzx}
    :param data:
    :return:
    """
    db,cursor = connect_mysql()
    k = ','.join(data.keys())
    v = ('%s,'*len(data))[:-1]
    sql = "INSERT INTO {t} ({k}) values ({v}) ON DUPLICATE KEY UPDATE ".format(t=table_name,k=k,v=v)
    update = ','.join( ["{} = %s".format(key) for key in data.keys()] )
    sql += update
    print(sql)
    print(tuple(data.values()) * 2)
    try:
        cursor.execute(sql, tuple(data.values()) * 2)
        db.commit()
        print('成功!')
    except Exception as e:
        print(e)
        db.rollback()
        print('失败')
        pass
    db.close()
    pass
def mysql_other_op(sql_sentence):
    print(sql_sentence)
    conn, cur =connect_mysql()
    try:
        cur.execute(sql_sentence)
        conn.commit()
        insert_id = cur.lastrowid
        print('成功执行语句')
    except Exception as e:
        conn.rollback()
        print(e)
        print('失败！！！')

    conn.close()
    return insert_id
if __name__ == '__main__':
    mysql_other_op('CREATE DATABASE IF NOT EXISTS ops_manage DEFAULT CHARSET utf8 COLLATE utf8_general_ci;')
    mysql_other_op('source ./ops_manage.sql')