from django.db import connection
from datetime import datetime
from datetime import date
import logging
from rest_framework import status as http_status
import re
import decimal

logger = logging.getLogger(__name__)


def to_camel(s):
    if '_' in s:
        s = re.sub(r"(\s|_|-)+", " ", s).title().replace(" ", "")
    else:
        return s
    return s[0].lower() + s[1:]


def to_underline(params: dict):
    '''
    将参数名的驼峰形式转为下划线形式
    @param params:
    @return:
    '''
    temp_dict = {}
    for name, value in params.items():
        temp_name = ""
        if re.search("[A-Z]", name):
            capital_letters = re.findall("[A-Z]", name)
            for c in capital_letters:
                lower_c = c.lower()
                r_str = "_" + lower_c
                temp_name = name.replace(c, r_str)
        else:
            temp_name = name

        temp_dict.update({temp_name: value})

    return temp_dict


def dict_query(sql, *args, camel=True):
    with connection.cursor() as cursor:
        logger.debug(f'in dict_query: sql is {sql}, args is {args}')
        cursor.execute(sql, *args)
        desc = cursor.description
        if camel:
            obj_list = [
                dict(zip([to_camel(col[0]) for col in desc], row))
                for row in cursor.fetchall()
            ]
        else:
            obj_list= [
                dict(zip([col[0] for col in desc], row))
                for row in cursor.fetchall()
            ]
        for item in obj_list:
            for key_, val_ in item.items():
                if isinstance(val_, datetime):
                    item[key_] = val_.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(val_, date):
                    item[key_] = val_.strftime('%Y-%m-%d')
                elif isinstance(val_, decimal.Decimal):
                    item[key_] = float(val_)
        return obj_list

def get_func(primary_key, query_params, condition_sql, params, table_name, selfields="*", camel=True):
    page_no = int(query_params.get('page', '1'))
    page_size = int(query_params.get('size', '5000000'))
    if page_no <= 0 or page_size <= 0:
        dict_ = {'status': 'fail', 'message': f'page{page_no} or size{page_size} is not in valid range.',
                 'data': [], 'count': 0}
        return dict_
    obj_id_query_sql = f'select `{primary_key}` from {table_name} '
    # print(f'obj_id_query_sql:{obj_id_query_sql}')
    # print(f'condition_sql:{condition_sql}')
    # print(f'params:{params}')
    query_sql = f'select {selfields} from {table_name} '
    total_cnt = dict_query("select count(1) cnt from ( " + obj_id_query_sql + condition_sql + " ) a ", params, camel=camel)[0][
        'cnt']
    if total_cnt == 0:
        dict_ = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [], 'count': total_cnt}
        return dict_
    # print(f'total_cnt:{total_cnt}')
    obj_list = dict_query(query_sql + condition_sql + ' order by updated_at desc limit %s,%s',
                          [*params, (page_no - 1) * page_size, page_size], camel=camel)


    dict_ = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': obj_list,
             'count': total_cnt}
    return dict_


def put_func(primary_key, request_data, model_obj, seria_obj, check_field=''):
    if check_field:
        if check_field == True:
            check_field = 'name'
        check_field_val = request_data.get(check_field)
    else:
        check_field_val = ''

    resp = {'status':'success'}
    id = request_data.get(primary_key)
    # first是从查询集中 获取一个model对象
    if id:
        dict_ = {primary_key: id}
        obj = model_obj.objects.filter(**dict_).first()
        ser = seria_obj(instance=obj, data=request_data)
        resp['is_new'] = False
    else:
        if check_field and check_field_val:
            try:
                flag_old = model_obj.objects.filter(**{check_field: check_field_val}).exists()
            except:
                flag_old = False
            if flag_old:
                raise Exception(f'{check_field}:{check_field_val} exsits')
        ser = seria_obj(data=request_data)
        resp['is_new'] = True

    # 传递 两个参数 参数1是要修改的数据  参数2是要赋予的新值

    if ser.is_valid():
        new_id = ser.save()
        resp['code'] = http_status.HTTP_200_OK
        resp['message'] = 'put ok'
        resp['data'] = new_id.id
    else:
        resp['code'] = http_status.HTTP_500_INTERNAL_SERVER_ERROR
        resp['message'] = ser.errors
    return resp


def delete_func(primary_key, obj_id, model_obj):
    if not obj_id:
        raise KeyError('obj_id missing in request.')

    if isinstance(obj_id, list):
        dict_ = {primary_key + '__in': obj_id}
    elif ',' in str(obj_id):
        dict_ = {primary_key + '__in': str(obj_id).split(',')}
    else:
        dict_ = {primary_key: int(obj_id)}

    if model_obj.objects.filter(**dict_).exists():
        model_obj.objects.filter(**dict_).delete()
    return {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'delete OK'}


def get_relative_func(primary_key, join_con, show_id, query_params, condition_sql, params, table_name, com_table,
                      selfields, camel=True, bagg='bid'):
    page_no = int(query_params.get('page', '1'))
    page_size = int(query_params.get('size', '999999'))
    dict_ = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [],
             'count': 0}
    if page_no <= 0 or page_size <= 0:
        dict_['status'] = 'fail'
        dict_['message'] = f'page{page_no} or size{page_size} is not in valid range.'
        return dict_
    obj_id_query_sql = f'select {primary_key} from {table_name} a left join {com_table} b on {join_con} '
    query_sql = f'''select  JSON_ARRAYAGG(JSON_OBJECT({show_id})) AS {bagg},{selfields} from {table_name} a left join {com_table} b on {join_con} {condition_sql} GROUP BY {primary_key} order by a.updated_at desc limit %s,%s '''
    total_cnt = \
    dict_query("select count(1) cnt from ( " + obj_id_query_sql + condition_sql + " ) a ", params, camel=camel)[0][
        'cnt']
    if total_cnt == 0:
        return dict_
    # print(query_sql)
    obj_list = dict_query(query_sql, [*params, (page_no - 1) * page_size, page_size], camel=camel)
    dict_['data'] = obj_list
    dict_['count'] = total_cnt
    return dict_
