# -*- coding: utf-8 -*-
import json
import time
import traceback
from datetime import datetime, timedelta
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.common.try_catch import try_catch
from rest_framework import status as http_status
import logging
import random
from django.forms.models import model_to_dict
from apps.common.utils import count_kuadu, alarm_format_time
from django.conf import settings
from .models import *
from apps.common.dbopr import dict_query
from apps.common.helpers import encrypt
from apps.om_alarm.celery_tasks.task import om_consumer_start
from .serializers import *
import copy
from .esQuery import EsOperation
from apps.common.dbopr import get_func, put_func, delete_func, get_relative_func
from apps.common.redisclient import RedisClient, get_alarm_id, get_all_black, set_identity_json, has_identity_json

logger = logging.getLogger(__name__)


# Create your views here.


class AlarmUserView(APIView):
    """
    告警联系人接口
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        isSelect = query_params.get('isSelect', False)
        if isSelect:
            obj_list = dict_query('select `username`,`name` from alarm_user', [], camel=False)
            res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': obj_list,
                        'count': len(obj_list)}
            return Response(res_dict, http_status.HTTP_200_OK)
        searchVal = query_params.get('searchVal', None)
        username = query_params.get('username', None)
        condition_sql = ' where 1=1 '
        params = []
        if username:
            condition_sql += ' and (`username`=%s) '
            params.extend([username])
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(`name`,%s) or instr(username,%s)  or instr(phone,%s) or instr(email,%s)) '
            params.extend([searchVal] * 4)

        res_dict = get_func('id', query_params, condition_sql, params, 'alarm_user', selfields="*", camel=False)

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        operate = request_data.get('operate', 'put')
        username = request_data.get('username')
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        if operate == 'add':
            check_field = 'username'
            request_data['created_by'] = login_user
            if not request_data.get('email'):
                request_data['email'] = request_data['username'] + f'@iflytek.com'
        else:
            check_field = ''
        resp = put_func('id', request_data, AlarmUser, AlarmUserer, check_field)
        if username:
            del_redis_cache('alarm_user', username)
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]
        usernames = [item['username'] for item in AlarmUser.objects.filter(id__in=deleteIds).values('username')]
        for username in usernames:
            del_redis_cache('alarm_user', username)
        resp = delete_func('id', deleteIds, AlarmUser)
        return Response(resp, http_status.HTTP_200_OK)


class AlarmConfigView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        srmid = query_params.get('id', None)
        condition_sql = ' where 1=1 '
        params = []
        if srmid:
            condition_sql += ' and (`id`=%s) '
            params.extend([srmid])

        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += 'and (instr(`id`,%s) or instr(name,%s) or instr(alarm_to,%s) or instr(rule_name,%s) or instr(`desc`,%s))'
            params.extend([searchVal] * 5)

        res_dict = get_func('id', query_params, condition_sql, params, 'alarm_config', selfields="*", camel=False)
        for item in res_dict['data']:
            alarm_to = json.loads(item.pop('alarm_to'))
            item['alarm_to'] = alarm_to
            label_send = json.loads(item.pop('label_send'))
            item['label_send'] = label_send
            alarm_detail = []
            for key_, val_ in alarm_to.items():
                if val_:
                    for smItem in val_:
                        alarm_detail.append({'alarm_type': key_, 'alarm_user': smItem['send_to']})
            item['alarm_detail'] = alarm_detail
        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        operate = request_data.get('operate', 'put')
        srmid = request_data.get('id')
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        if operate == 'add':
            check_field = 'id'
            request_data['created_by'] = login_user
        else:
            check_field = ''
        resp = put_func('id', request_data, AlarmConfig, AlarmConfiger, check_field)
        if srmid:
            del_redis_cache('alarm_config', srmid)
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]
        for srmid in deleteIds:
            del_redis_cache('alarm_config', srmid)

        resp = delete_func('id', deleteIds, AlarmConfig)
        return Response(resp, http_status.HTTP_200_OK)


class AlarmRuleView(APIView):
    """
    告警rule接口
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        isSelect = query_params.get('isSelect', False)
        if isSelect:
            obj_list = dict_query('select `name` from alarm_rule', [], camel=False)
            res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': obj_list,
                        'count': len(obj_list)}
            return Response(res_dict, http_status.HTTP_200_OK)
        searchVal = query_params.get('searchVal', None)
        name = query_params.get('name', None)
        condition_sql = ' where 1=1 '
        params = []
        if name:
            condition_sql += ' and (`a.name`=%s) '
            params.extend([name])
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(a.name,%s) or instr(a.freq,%s)  or instr(a.desc,%s) or instr(a.rule_keys,%s) or b.id=%s) '
            params.extend([searchVal] * 5)
        res_dict = get_relative_func('a.id', 'a.name=b.rule_name', '"id",b.id', query_params,
                                     condition_sql, params, 'alarm_rule', 'alarm_config',
                                     'a.*', camel=False, bagg='configIds')
        for item in res_dict['data']:
            configIds = json.loads(item.pop('configIds'))
            item['configIds'] = [val['id'] for val in configIds]
        # res_dict = get_func('id', query_params, condition_sql, params, 'alarm_rule', selfields="*", camel=False)

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        operate = request_data.get('operate', 'put')
        name = request_data.get('name')
        rule_id = request_data.get('id')
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        if operate == 'add':
            check_field = 'name'
            request_data['created_by'] = login_user
        else:
            check_field = ''
        if rule_id:
            try:
                originObj = AlarmRule.objects.get(id=rule_id)
                originName = originObj.name
                if originName != name:
                    AlarmConfig.objects.filter(rule_name=originName).update(rule_name=name)
            except Exception as e:
                logger.error(f'update config rule name err:{e}')
        resp = put_func('id', request_data, AlarmRule, AlarmRuleer, check_field)
        if name:
            del_redis_cache('alarm_rule', name)
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]
        ruleNames = [item['username'] for item in AlarmRule.objects.filter(id__in=deleteIds).values('name')]
        for name in ruleNames:
            del_redis_cache('alarm_rule', name)
        resp = delete_func('id', deleteIds, AlarmRule)
        return Response(resp, http_status.HTTP_200_OK)

SEVERITY_DICT = {
    'info':'一般',
    'normal':'一般',
    'warn':'警告',
    'critical':'严重',
    '重要':'严重',
    'disaster':'灾难',
    'urgent':'紧急',
}

class AlarmReceiverView(APIView):
    '''
    针对labels 中字段可以做分类统计
    {
    "status": "firing",# resolved,firing ,默认firing
    "mustAlert": False,# 必须告警，每一次必须告警，不收敛，默认False，可写在labels内
    "alert_start": "08:00",# 选填，可写在labels内
    "alert_end": "21:00",# 选填，可写在labels内
    "labels": {
        "id":601,#告警id
        "severity":"一般",#一般，警告，严重，紧急，灾难
        "alertname":"cpu使用率过高",#告警名或脚本名
        "job":"aops-tengine",#项目组件等
        "group":"节点监控",#分组，选填
        "source":"10.110.1.14:9093",#来源，选填
        "instance":"10.110.1.18",#选填，实例
        "time_range":"24",#选填，12为白天告警，243为全天告警
    },
    "annotations": {
        "summary": "测试告警001",
        "description": "测试告警001-desc",
        }
    }
    '''

    def get_graph_url(self, old_url):
        new_url = ''
        # 使用正则表达式提取 node_ 后面的 IP 地址部分
        match = re.search(r"http.*node_([\d_]+?):", old_url)
        if match:
            node_ip = match.group(1)
            node_real_ip = node_ip.replace("_", ".")
            new_url = old_url.replace(f"node_{node_ip}", node_real_ip)
        else:
            new_url = old_url
        return new_url

    def deploy_alert(self, alert, alertIdsDict={}, black_re_str='', externalURL=''):
        resp_data = {'status': 'success', 'msg': '', 'queue_data': {}}
        try:
            srmid = alert['labels'].get('id', 1)
            # 统一id int
            severity = alert['labels'].get('severity','一般')
            if severity in SEVERITY_DICT.keys():
                alert['labels']['severity'] = SEVERITY_DICT[severity]

            alert['labels']['id'] = int(srmid)
            if alert['labels'].get('srmid'):
                alert['labels']['id'] = int(alert['labels'].get('srmid'))
            source = alert['labels'].get('source', '')
            if not source:
                source = externalURL
            generatorURL = self.get_graph_url(alert.get('generatorURL', ''))
            mustAlert = alert.get('mustAlert', False)
            if 'mustAlert' in alert['labels'].keys():
                mustAlert = alert['labels'].pop('mustAlert')
                if str(mustAlert) == '1':
                    mustAlert = True
                elif str(mustAlert) == '0':
                    mustAlert = False

            alert['labels'].update({
                'id': srmid,
                'source': source,
                'alert_url': externalURL,
                'graph_url': generatorURL,
            })
            post_data = {
                'startsAt': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': alert.get('status', 'firing'),
                'mustAlert': mustAlert,
                'labels': alert['labels'],
                'customSend': alert.get('customSend',{}),
                'annotations': {
                    'summary': alert['annotations'].get('summary', ''),
                    'description': f"{alert['annotations'].get('description', '')}{alert['annotations'].get('message', '')}",
                }
            }
            if 'time_range' in alert['labels'].keys():
                time_range = alert['labels'].pop('time_range')
                if str(time_range) == '24':
                    post_data['alert_start'] = '00:00'
                    post_data['alert_end'] = '23:59'
                elif str(time_range) == '12':
                    post_data['alert_start'] = '09:00'
                    post_data['alert_end'] = '21:00'
            if 'alert_start' in alert['labels'].keys():
                post_data['alert_start'] = alert['labels'].pop('alert_start')
            if 'alert_end' in alert['labels'].keys():
                post_data['alert_end'] = alert['labels'].pop('alert_end')

            srmid = post_data['labels']['id']

            if alertIdsDict:
                alarm_id_dict = alertIdsDict[int(srmid)]
            else:
                alarm_id_dict = get_alarm_id(srmid)

            if not alarm_id_dict:
                resp_data['status'] = 'error'
                resp_data['msg'] = f'no alarm_id:{srmid}'
                return resp_data

            # labels 中 或者alert中都没有alert_start 等，就从alarm_id 中看有无，有就添加上
            if (not 'alert_start' in post_data.keys()) and alarm_id_dict.get('alert_start'):
                post_data['alert_start'] = alarm_id_dict.get('alert_start')
            if (not 'alert_end' in post_data.keys()) and alarm_id_dict.get('alert_end'):
                post_data['alert_end'] = alarm_id_dict.get('alert_end')

            # 检查alert_start 格式
            if 'alert_start' in post_data.keys():
                alert_start = post_data.get('alert_start')
                try:
                    time.strptime(alert_start, '%H:%M')
                except:
                    post_data.pop('alert_start')
                    logger.error(f'alert_start format err:{alert_start}')
            if 'alert_end' in post_data.keys():
                alert_end = post_data.get('alert_end')
                try:
                    time.strptime(alert_end, '%H:%M')
                except:
                    post_data.pop('alert_end')
                    logger.error(f'alert_start format err:{alert_end}')

            nowtime = time.strftime("%H:%M")
            # 不在告警时间段内
            if not (post_data.get('alert_start', '00:00') <= nowtime and nowtime <= post_data.get('alert_end',
                                                                                                  '23:59')):
                resp_data['status'] = 'warn'
                resp_data['msg'] = 'not in time_field'
                logger.warning(f'not in time_field:{post_data}')
                return resp_data
            description = f"summary:{post_data['annotations'].get('summary','')},desc:{post_data['annotations'].get('description','')}"
            if black_re_str and description:
                resp = re.search(black_re_str, description)
                if resp:
                    resp_data['status'] = 'warn'
                    resp_data['msg'] = 'desc in black list'
                    logger.warning(f'desc in black list:{post_data}')
                    return resp_data

            post_data['alarm_id_dict'] = alarm_id_dict
            queue_data = {'id': srmid, 'queue': 'ops_alarm_consumer', 'post_data': encrypt(post_data)}
            resp_data['queue_data'] = queue_data
        except Exception as e:
            resp_data['status'] = 'error'
            resp_data['msg'] = str(e)
            logger.error(traceback.format_exc())
        return resp_data

    def deploy_send(self, resp_data, dict_):
        resp_status = resp_data['status']
        if resp_status == 'success':
            om_consumer_start(**resp_data['queue_data'])

        if resp_status == 'success':
            dict_['okCnt'] += 1
        elif resp_status == 'error':
            dict_['errCnt'] += 1
            dict_['message'] += resp_data['msg'] + '\n'
        elif resp_status == 'warn':
            dict_['warnCnt'] += 1
            dict_['message'] += resp_data['msg'] + '\n'
        return dict_

    def get_all_black_valid(self):
        timeNow = time.strftime('%Y-%m-%d %H:%M:%S')
        all_black_list = get_all_black()
        black_re_list = []
        for item in all_black_list:
            black_valid = True
            black_to = item.get('black_to')
            if black_to:
                try:
                    if datetime.strptime(timeNow, '%Y-%m-%d %H:%M:%S') >= datetime.strptime(black_to,
                                                                                            '%Y-%m-%d %H:%M:%S'):
                        black_valid = False
                except Exception as e:
                    black_valid = False
                    logger.error(f'ignore_to err:{e}')
            if black_valid and item.get('rule_re'):
                black_re_list.append(item.get('rule_re'))
        return '|'.join(black_re_list)

    @try_catch
    def post(self, request):
        dict_ = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': '', 'data': [],
                 'okCnt': 0, 'errCnt': 0, 'warnCnt': 0}
        request_data = request.data
        logger.info(f'recv>>>:{request_data}')
        alerts = request_data.get('alerts', [])
        black_re_str = self.get_all_black_valid()
        externalURL = request_data.get('externalURL', '').replace('node_', '').replace('_', '.')
        if alerts:
            # prometheus 告警
            # 加速，去重id
            alertIds = set()
            for alert in alerts:
                srmid = alert['labels'].get('id', 1)
                if alert['labels'].get('srmid'):
                    srmid = int(alert['labels'].get('srmid'))
                # 统一id int
                alertIds.add(int(srmid))

            alertIdsDict = {}
            for alertId in alertIds:
                alertIdsDict[alertId] = get_alarm_id(alertId)

            for alert in alerts:
                resp_data = self.deploy_alert(alert, alertIdsDict, black_re_str, externalURL)
                dict_ = self.deploy_send(resp_data, dict_)
                # time.sleep(random.uniform(0.1, 0.5))
        else:
            # 单个告警
            alert = request_data
            resp_data = self.deploy_alert(alert=alert, black_re_str=black_re_str, externalURL=externalURL)
            dict_ = self.deploy_send(resp_data, dict_)

        if dict_['errCnt'] > 0:
            logger.error(f'alert has err:{dict_}')
        return Response(dict_, http_status.HTTP_200_OK)


class CacheReadlView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        resp = {}
        query_params = request.query_params.dict()
        datatype = query_params.get('datatype', 'markdown')
        resp_data = CacheRead.objects.filter(datatype=datatype)
        if resp_data:
            resp_data = resp_data[0].cachestr
        else:
            resp_data = ''
        resp['code'] = http_status.HTTP_200_OK
        resp['code'] = http_status.HTTP_200_OK
        resp['data'] = resp_data
        return Response(resp,
                        http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        resp = {}
        logger.info("request.data:%s", request.data)
        request_data = request.data
        datatype = request_data.get('datatype', 'markdown')
        cachestr = request_data.get('cachestr')
        # first是从查询集中 获取一个model对象
        try:
            obj = CacheRead.objects.filter(datatype=datatype).first()
            if cachestr:
                if obj:
                    # 传递 两个参数 参数1是要修改的数据  参数2是要赋予的新值
                    obj.cachestr = cachestr
                    obj.save()
                    logger.debug('put ok')
                else:
                    CacheRead.objects.create(datatype=datatype, cachestr=cachestr)
                    logger.debug('post ok')
        except Exception as e:
            resp['code'] = http_status.HTTP_500_INTERNAL_SERVER_ERROR
            resp['message'] = str(e)
        resp['code'] = http_status.HTTP_200_OK
        resp['message'] = 'put ok'

        return Response(resp, http_status.HTTP_200_OK)


class AlarmBlackView(APIView):
    """
    告警黑名单
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        id = query_params.get('id', None)
        condition_sql = ' where 1=1 '
        params = []
        if id:
            condition_sql += ' and (`id`=%s) '
            params.extend([id])
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(`name`,%s) or instr(rule_re,%s) or instr(desc,%s) ) '
            params.extend([searchVal] * 3)

        res_dict = get_func('id', query_params, condition_sql, params, 'alarm_black', selfields="*", camel=False)

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, AlarmBlack, AlarmBlacker)
        del_redis_cache('alarm_black', 'all')
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]
        del_redis_cache('alarm_black', 'all')
        resp = delete_func('id', deleteIds, AlarmBlack)
        return Response(resp, http_status.HTTP_200_OK)


def convert_to_han_time(time_str):
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
        return f"{days}天{hours}时{minutes}分"
    elif hours > 0:
        return f"{hours}时{minutes}分"
    elif minutes > 0:
        return f"{minutes}分"
    else:
        return "刚刚"


def del_redis_cache(prifix, key_str):
    try:
        r = RedisClient('dbalarm').client
        del_keys = r.keys(f'{prifix}:{key_str}')
        if del_keys:
            r.delete(*del_keys)
    except Exception as e:
        logger.warning(f'del {prifix} err:{e}')


class AlarmIdentityInfoView(APIView):
    "告警指纹"

    @try_catch
    def get(self, request):
        data = request.query_params
        logger.debug(data)
        identity_id = data.get("id", "")
        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': f'OK'}
        if not identity_id:
            resp['status'] = 'fail'
            resp['message'] = 'id null'
            return Response(resp, http_status.HTTP_200_OK)
        identity_id = int(identity_id)
        resp_list = AlarmIdentity.objects.filter(id=identity_id).values()
        resp_info = {}
        if resp_list:
            resp_info = resp_list[0]
        resp['data'] = resp_info
        resp['count'] = 1
        resp['message'] = 'successful'
        return Response(resp, http_status.HTTP_200_OK)


class AlarmIdentityResourceView(APIView):
    "告警指纹"

    @try_catch
    def get(self, request):
        data = request.query_params
        logger.debug(data)
        searchType = data.get("searchType", "activate")
        searchTime = data.get("searchTime", '').split(',')
        updateSearchTime = data.get("updateSearchTime", '').split(',')
        identity_tag = data.get("searchVal", "")
        identity_id = data.get("id", "")
        field = data.get("orderField", "")
        status = data.get("status", "")
        order = data.get("orderType", "descend")

        # sql origin
        page_size = int(data.get("size", 10))
        page_no = int(data.get("page", 1))
        user_query_sql = 'select a.*,timestampdiff(MINUTE,a.created_at,NOW()) as process_time from alarm_identity a '
        obj_id_query_sql = 'select a.id from alarm_identity a '
        if searchType == 'activate':
            condition_sql = ' where status!=0 '
        elif searchType == 'deactivate':
            # 搜索历史告警
            condition_sql = ' where status=0 '
        else:
            condition_sql = ' where 1=1 '
        params = []
        if searchTime:
            try:
                create_start = searchTime[0]

                if create_start:
                    condition_sql += ' and (a.created_at>=%s) '
                    params.append(create_start)

                create_end = searchTime[1]
                if create_end:
                    condition_sql += ' and (a.created_at<=%s) '
                    params.append(create_end)
            except Exception as e:
                pass
        if updateSearchTime:
            try:
                update_start = updateSearchTime[0]
                if update_start:
                    condition_sql += ' and (a.updated_at>=%s) '
                    params.append(update_start)
                update_end = updateSearchTime[1]
                if update_end:
                    condition_sql += ' and (a.updated_at<=%s) '
                    params.append(update_end)
            except Exception as e:
                pass

        if identity_tag:
            condition_sql += ' and (instr(a.identity_tag_kv,%s)) '
            params.extend(["{}".format(identity_tag)])
        if identity_id:
            condition_sql += ' and (a.id=%s) '
            params.extend(["{}".format(identity_id)])
        if status:
            status = status.replace('"', '').replace("'", '')
            condition_sql += f' and status in ({status}) '
        total_cnt = dict_query(
            "select count(1) cnt from ( " + obj_id_query_sql + condition_sql +
            " ) a ", params)[0]['cnt']
        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [], 'count': 0}
        if total_cnt == 0:
            return Response(resp, http_status.HTTP_200_OK)

        order_str = ''
        if field:
            order = 'asc' if order == 'ascend' else 'desc'
            order_str = field + ' ' + order + ', '
        resp_list = dict_query(
            user_query_sql + condition_sql +
            ' order by ' + order_str + 'updated_at desc' + ' limit %s,%s',
            [*params, (page_no - 1) * page_size, page_size], camel=False)
        alertIds = set()
        for item in resp_list:
            item['duration_time'] = convert_to_han_time(item.get('created_at'))
            identity_tag_kv = json.loads(item.pop('identity_tag_kv'))
            item['identity_tag_kv'] = identity_tag_kv
            if 'id' in identity_tag_kv.keys():
                alertId = identity_tag_kv.get('id')
                alertIds.add(alertId)

        alertIdsDict = {}
        for alertId in alertIds:
            alertInfo = get_alarm_id(alertId)
            alarm_to = alertInfo.get('alarm_to', {})
            alarm_detail = []
            for key_, val_ in alarm_to.items():
                if val_:
                    for smItem in val_:
                        alarm_detail.append({'alarm_type': key_, 'alarm_user': smItem['send_to']})
            alertInfo['alarm_detail'] = alarm_detail
            alertIdsDict[alertId] = alertInfo

        # 丰富字段
        for item in resp_list:
            identity_tag_kv = item['identity_tag_kv']
            alertId = identity_tag_kv.get('id')
            srmidInfo = {}
            if alertId:
                srmidInfo = alertIdsDict.get(alertId)
            item['srmidInfo'] = srmidInfo
        resp['data'] = resp_list
        resp['count'] = total_cnt
        resp['message'] = 'successful'
        return Response(resp, http_status.HTTP_200_OK)

    def add_comment(self, identity_id, request_data, login_user):
        try:
            statusDict = {
                0: '消除',
                1: '正在处理',
                2: '处理完成',
                3: '暂时忽略',
                4: '未处理',
                5: '自动恢复',
            }
            status = request_data.get('status', 1)
            if status == 3:
                comment_text = f"暂时忽略;{request_data.get('ignore_to', '')}"
            else:
                comment_text = statusDict.get(int(status), '正在处理')
            comment_content = {
                "comment_text": "修改状态<br>"
                                f"&nbsp;&nbsp; 处理流程:{comment_text};<br>"
                                f"&nbsp;&nbsp; 处理人:{request_data.get('handler', '')}",
                "comment_type": "status",
            }

            if isinstance(identity_id, list):
                ls_create = []
                for x in identity_id:
                    dict_ = {
                        'identity_id': x,
                        'comment_content': comment_content,
                        'operator': login_user,
                    }
                    ls_create.append(AlarmComment(**dict_))

                if ls_create:
                    AlarmComment.objects.bulk_create(ls_create)
            else:
                add_data = AlarmComment.objects.create(
                    identity_id=identity_id,
                    comment_content=comment_content,
                    operator=login_user,
                )
                add_data.pre_comment = add_data
                add_data.save()
        except Exception as e:
            logger.error(f'add comment err:{e}')

    @try_catch
    def post(self, request):
        '''
        '''
        request_data = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        login_realname = request.realname if hasattr(request, 'realname') else 'sys'

        logger.info(f"identity operate by:{login_user},request_data:{request_data}")
        postIds = request_data.get('postIds', [])
        opType = request_data.get('opType', '')

        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': f'{opType} OK'}
        if not postIds:
            postIds = [request_data['id']]

        if opType == 'deactivate':
            # 记录到评论中
            self.add_comment(postIds, request_data, login_realname)

            identities = [item['identity'] for item in AlarmIdentity.objects.filter(id__in=postIds).values('identity')]
            for kv_md5 in identities:
                del_redis_cache('alarm_identity', kv_md5)
                del_redis_cache('alarm_resolved', kv_md5)
                del_redis_cache('alarm_zhiwen', kv_md5)

            dict_ = {'id__in': postIds}
            AlarmIdentity.objects.filter(**dict_).update(status=0)
        elif opType == 'modifyStatus':
            status = request_data.get('status', AlarmIdentity.Status.UNDISPOSED[0])

            # 记录到评论中
            self.add_comment(postIds, request_data, login_realname)
            flag_update = True
            forbit_msg = ''
            if status == AlarmIdentity.Status.DISARBLE[0]:
                identities = [item['identity'] for item in
                              AlarmIdentity.objects.filter(id__in=postIds).values('identity')]
                for kv_md5 in identities:
                    del_redis_cache('alarm_identity', kv_md5)
                    del_redis_cache('alarm_resolved', kv_md5)
                    del_redis_cache('alarm_zhiwen', kv_md5)
            else:
                identity_list = AlarmIdentity.objects.filter(id__in=postIds).values()
                for identity_json in identity_list:
                    identity = identity_json['identity']
                    origin_status = identity_json['status']
                    #从销毁改到存活需要检查
                    # print('origin_status>>>',origin_status,status,identity)
                    if origin_status == 0 and status!=0:
                        # print('select id from alarm_identity where status!=0 and identity=%s ')
                        exists_list = dict_query('select id from alarm_identity where status!=0 and identity=%s ',[identity], camel=False)
                        # print('exists_list>>>',exists_list)
                        if exists_list:
                            flag_update = False
                            forbit_msg = f'重新存活{identity_json.get("id","")}失败！存活指纹中已存在{identity_json.get("identity_tag_kv","")}'
                            break
                if flag_update:
                    for identity_json in identity_list:
                        created_at = identity_json['created_at']
                        updated_at = identity_json['created_at']
                        ignore_to = identity_json['ignore_to']
                        if isinstance(ignore_to, datetime):
                            identity_json['ignore_to'] = ignore_to.strftime('%Y-%m-%d %H:%M:%S')
                        if isinstance(updated_at, datetime):
                            identity_json['updated_at'] = updated_at.strftime('%Y-%m-%d %H:%M:%S')
                        if isinstance(created_at, datetime):
                            identity_json['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
                        identity_json.update({
                            'status': status,
                            'ignore_to': request_data.get('ignore_to', ''),
                            'record_ignore': request_data.get('record_ignore', 1),
                        })
                        set_identity_json(identity, identity_json)

            if flag_update:
                dict_ = {'id__in': postIds}
                updateData = {
                    'status': status,
                    'handler': request_data.get('handler', ''),
                    'ignore_to': request_data.get('ignore_to', ''),
                    'record_ignore': request_data.get('record_ignore', 1)
                }

                AlarmIdentity.objects.filter(**dict_).update(**updateData)
            else:
                resp['status'] = 'fail'
                resp['code'] = 500
                resp['message'] = forbit_msg
                return Response(resp, http_status.HTTP_200_OK)
        elif opType == 'reagg':
            identities = [item['identity'] for item in AlarmIdentity.objects.filter(id__in=postIds).values('identity')]
            for kv_md5 in identities:
                del_redis_cache('alarm_identity', kv_md5)
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [], 'count': 0}
        request_data = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        user = request.realname if hasattr(request, "realname") else "ApiToken"
        identity_id = request_data.pop("id", "")
        status = request_data.get("status", 1)

        if identity_id is None:
            resp['status'] = 'fail'
            resp['message'] = 'identity_id is None'
            return Response(resp, status=http_status.HTTP_200_OK)

        update_data = AlarmIdentity.objects.filter(
            id=identity_id).first()
        if update_data and status:
            # 消除前检查备注
            if status == 2:
                comment_list = AlarmComment.objects.filter(identity_id=identity_id,
                                                           comment_content__comment_type='text')
                print('comment_list>>>', comment_list)
                if not comment_list:
                    raise Exception('消除前至少有一条备注')

            update_data.status = status
            update_data.operator = user
            update_data.save()
            resp['message'] = 'successful'
            resp['data'] = model_to_dict(update_data)
        else:
            resp['data'] = {}
            resp['message'] = 'successful'

        return Response(resp, http_status.HTTP_200_OK)


def list_to_tree(data):
    root = []
    node = []

    for i in data:

        if i.get("id", 0) == i.get("pre_comment", 0):
            root.append(i)
        elif not i.get("pre_comment"):
            root.append(i)
        else:
            node.append(i)
    [add_node(p, node) for p in root]
    if not root:
        return node
    return root


def add_node(p, node):
    p["children"] = [n for n in node if n.get(
        "pre_comment", 0) == p.get("id", 0)]
    [t.setdefault("children", []).append(add_node(t, node))
     for t in p["children"]]

    if not p["children"]:
        return


class AlarmCommentResoureView(APIView):
    @try_catch
    def get(self, request):

        data = request.query_params
        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': f'OK'}
        realname = request.realname if hasattr(request, "realname") else "system"
        logger.debug(data)
        identity_id = data.get("identity_id", 0)
        if identity_id:
            alarm_comment = AlarmComment.objects.filter(
                identity_id=identity_id).all()
            alarm_comment = AlarmCommenter(alarm_comment, many=True)
            alarm_comment_data = alarm_comment.data
            logger.debug(alarm_comment_data)
            # print('alarm_comment_data>>>',alarm_comment_data)
            tree_data = list_to_tree(alarm_comment_data)
            # print('tree_data>>>',tree_data)
            resp['data'] = tree_data
            resp['login_user'] = realname
            resp['count'] = len(alarm_comment_data)

        else:
            resp['data'] = []
            resp['login_user'] = ''
            resp['count'] = 0

        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def post(self, request):
        data = request.data
        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': f'OK'}
        user = request.realname if hasattr(request, "realname") else "system"

        identity = data.get("identity_id", 0)
        pre_comment = data.get("pre_comment", 0)

        comment_text = data.get("comment_text", "")

        pre_comment_data = AlarmComment.objects.filter(
            id=pre_comment).first()

        # issue_id = ""

        comment_content = {
            "comment_text": comment_text,
            "comment_type": "text",
        }

        add_data = AlarmComment.objects.create(
            identity_id=identity,
            comment_content=comment_content,
            operator=user
        )
        if pre_comment_data:
            add_data.pre_comment = pre_comment_data
        else:
            add_data.pre_comment = add_data

        add_data.save()
        resp['data'] = model_to_dict(add_data)

        return Response(resp, http_status.HTTP_200_OK)


class AlarmSolutionView(APIView):

    @try_catch
    def get(self, request):
        data = request.query_params
        alarmId = data.get("identity_id", 0)
        alarmSolution = {}
        if alarmId:
            alarm_solution_list = AlarmZongjie.objects.filter(identity_id=int(alarmId)).values()
            if alarm_solution_list:
                alarmSolution = alarm_solution_list[0]
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': alarmSolution,
                    'count': 1}

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        logger.info("request.data:%s", request.data)
        request_data = request.data
        identity_id = request_data.get('identity_id', 0)
        if identity_id:
            login_user = request.username if hasattr(request, 'username') else 'sys'
            request_data['updated_by'] = login_user
            put_data = {
                'identity_id': identity_id,
                'reach': request_data.get('reach', ''),
                'reason': request_data.get('reason', ''),
                'solution': request_data.get('solution', ''),
                'updated_by': login_user,
            }
            resp = put_func('identity_id', put_data, AlarmZongjie, AlarmZongjieer)
        else:
            raise Exception('no identity_id')
        return Response(resp, http_status.HTTP_200_OK)


def alarm_common_deploy_data(post_data, aggs, respKey='buckets'):
    time_field = 'startsAt'

    es_host = settings.ES_HOSTS
    es_username = settings.ES_USERNAME
    es_pwd = settings.ES_PWD
    es = EsOperation(es_host, es_username, es_pwd)
    post_data['index_str'] = 'opsalarm-*'
    post_data['time_field'] = time_field
    aggs_str = json.dumps(aggs)
    if '$timestamp$' in aggs_str:
        aggs = json.loads(aggs_str.replace('$timestamp$', time_field))

        # 预处理数据
        post_data = es.es_alarm_deploy(post_data, aggs=aggs)
        es_resp = es.es_alarmapi(post_data)
        resp_data = es_resp['aggregations'].get('resp', {}).get(respKey, [])
    else:
        resp_data = []
    return resp_data


def alarm_query_deploy_data(post_data, excludes=True):
    time_field = 'startsAt'

    es_host = settings.ES_HOSTS
    es_username = settings.ES_USERNAME
    es_pwd = settings.ES_PWD
    es = EsOperation(es_host, es_username, es_pwd)
    # beg_time = datetime.now()
    # end_time = datetime.now()
    # time_dtt = str((end_time - beg_time).total_seconds())
    # print('haoshi111>>>', time_dtt)
    post_data['index_str'] = 'opsalarm-*'
    post_data['time_field'] = time_field

    # 预处理数据
    timeSorter = post_data.get('timeSorter', 'descend')
    # prev 上一页 上拉获取一页数据，配合search_after,结果逆序下
    scrollType = post_data.get('scrollType', 'next')
    timeSorterDict = {
        'descend': 'desc',
        'ascend': 'asc',
    }
    reverseTimeSorterDict = {
        'descend': 'asc',
        'ascend': 'desc',
    }
    if scrollType == 'prev':
        time_order = reverseTimeSorterDict[timeSorter]
    else:
        time_order = timeSorterDict[timeSorter]
    post_data['sort'] = {
        post_data['time_field']: {
            "order": time_order
        },
        "_id": {
            "order": 'desc' if scrollType == 'prev' else 'asc'
        }
    }
    if excludes:
        post_data['_source'] = {
            "excludes": [
                "identity_tag_kv",
                "alertname",
                "job",
                "instance",
                "source",
                "group",
            ]
        }

    post_data = es.es_alarm_deploy(post_data)

    resp_data = es.es_alarmapi(post_data, allHits=True)
    return resp_data, time_field


class AlarmHistoryGramAggView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        searchTime = request_data['searchTime']
        step, formatstr = count_kuadu(searchTime[0], searchTime[1])
        aggs = {
            "resp": {
                "date_histogram": {
                    "field": "$timestamp$",
                    "fixed_interval": step,
                    "format": "epoch_millis"
                }
            }

        }
        logger.info("request_data:%s", request_data)
        resp_data = alarm_common_deploy_data(request_data, aggs)
        resp_data_pro = []
        for item in resp_data:
            timestr = alarm_format_time(item['key_as_string'], formatstr, add_time=False)
            dict_ = {
                'name': timestr,
                'value': item.get('doc_count', ''),
            }
            resp_data_pro.append(dict_)
        res_dict['data'] = resp_data_pro

        return Response(res_dict, http_status.HTTP_200_OK)


class AlarmSearchView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        logger.info("request_data:%s", request_data)
        historyPage = request_data.get('page', 1)
        scrollType = request_data.get('scrollType', 'next')
        resp_data, time_field = alarm_query_deploy_data(request_data)

        res_dict['count'] = resp_data.get('total', 0)
        resp_pro_list = []
        for item in resp_data['data']:
            event_dict = item['_source']

            dict_ = {
                '_id': item.get('_id', ''),
                'search_after': item.get('sort', []),
                'message': event_dict,
            }
            resp_pro_list.append(dict_)
        if scrollType == 'prev':
            resp_pro_list.reverse()
        res_dict['data'] = resp_pro_list
        res_dict['historyPage'] = historyPage

        return Response(res_dict, http_status.HTTP_200_OK)


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


class AlarmLastSilmilarView(APIView):

    @try_catch
    def post(self, request):
        data = request.data
        alarmId = data.get("alarm_id", 0)
        my_update_time = data.get("updated_at", '').replace('T', ' ')
        identity_dict = data.get("identity_dict", '')

        similar_item = {}
        similarIds = []
        if alarmId:
            # 根据identity_tagkv 寻找 相似
            # similar_query_sql = "select date_format(updated_at,%s) as updated_at,id from alarm_identity "
            similar_query_sql = "select updated_at,id,handler from alarm_identity "
            similar_condition_sql = ' where 1=1 '
            similar_params = []
            # similar_params.extend(["{}".format('%Y-%m-%d %H:%i:%s')])
            # recent 30 day
            offset = timedelta(days=30)
            fromtime = (datetime.strptime(my_update_time, '%Y-%m-%d %H:%M:%S') - offset).strftime('%Y-%m-%d %H:%M:%S')
            endtime = my_update_time
            similar_condition_sql += 'and ( updated_at>=%s and updated_at<%s )'
            similar_params.extend([fromtime, endtime])

            # 不是未处理的相似
            similar_condition_sql += ' and status!=4 '

            all_tag_patch = ' and instr(identity_tag_kv,%s) '
            # print('identity_dict>>>',identity_dict)
            similar_condition_sql += all_tag_patch
            similar_params.extend(["{}".format(identity_dict)])
            # print(similar_query_sql + similar_condition_sql + 'order by updated_at desc limit 6',)
            # print(similar_params)
            similar_list = dict_query(
                similar_query_sql + similar_condition_sql + 'order by updated_at desc limit 6',
                [*similar_params], camel=False)
            # print('oring similar_list>>>', similar_list)

            if not similar_list:
                similar_condition_sql = similar_condition_sql.replace(all_tag_patch, '')
                similar_params = similar_params[:-1]
                # kuo da fan wei
                again_excute_flag = False
                job = identity_dict.get('job', '')
                group = identity_dict.get('group', '')
                alertname = identity_dict.get('alertname', '')
                try:
                    if alertname:
                        again_excute_flag = True
                        now_condition_slq = similar_condition_sql + " and (JSON_EXTRACT(identity_tag_kv,'$.alertname')=%s )"
                        # similar_condition_sql += " and (JSON_EXTRACT(identity_tag_kv,'$.alertname')=%s )"
                        # similar_params.extend([alertname])
                        now_similar_params = similar_params+[alertname]
                        sm_similar_list = dict_query(
                            similar_query_sql + now_condition_slq + 'order by updated_at desc limit 6',
                            [*now_similar_params], camel=False)
                        similar_list.extend(sm_similar_list)

                    if job and len(similar_list) < 6:
                        again_excute_flag = True
                        now_condition_slq = similar_condition_sql + " and (JSON_EXTRACT(identity_tag_kv,'$.job')=%s )"
                        # similar_condition_sql += " and (JSON_EXTRACT(identity_tag_kv,'$.job')=%s )"
                        # similar_params.extend([job])
                        now_similar_params = similar_params + [job]
                        sm_similar_list = dict_query(
                            similar_query_sql + now_condition_slq + 'order by updated_at desc limit 6',
                            [*now_similar_params], camel=False)
                        similar_list.extend(sm_similar_list)
                    if group and len(similar_list) < 3:
                        again_excute_flag = True
                        now_condition_slq = similar_condition_sql + " and (JSON_EXTRACT(identity_tag_kv,'$.group')=%s )"
                        # similar_condition_sql += " and (JSON_EXTRACT(identity_tag_kv,'$.group')=%s )"
                        # similar_params.extend([group])
                        now_similar_params = similar_params + [group]
                        sm_similar_list = dict_query(
                            similar_query_sql + now_condition_slq + 'order by updated_at desc limit 6',
                            [*now_similar_params], camel=False)
                        similar_list.extend(sm_similar_list)
                except Exception as e:
                    print(traceback.format_exc())

                # if again_excute_flag:
                # print('again_excute_flag>>>',similar_query_sql+similar_condition_sql+'order by updated_at desc limit 6')
                # print(similar_params)
                # similar_list = dict_query(
                #     similar_query_sql + similar_condition_sql + 'order by updated_at desc limit 6',
                #     [*similar_params],camel=False)
                # print('again exec :',similar_list)
                set_similar_list = []
                set_id = set()
                for similarItem in similar_list:
                    similar_id = similarItem['id']
                    if not similar_id in set_id:
                        set_id.add(similar_id)
                        set_similar_list.append(similarItem)
                similar_list = set_similar_list


            if similar_list:
                similarIds = [item['id'] for item in similar_list[:6]]
                similar_item = similar_list[0]
                similar_id = similar_item['id']
                similar_update_time = similar_item['updated_at']
                similar_handler = similar_item['handler']

                note_query_sql = "select JSON_UNQUOTE(JSON_EXTRACT(comment_content,'$.comment_text')) as comment_text,operator from alarm_comment "
                note_condition_sql = " where identity_id=%s and JSON_EXTRACT(comment_content,'$.comment_type')='text' "
                note_params = [similar_id]
                note_list = dict_query(
                    note_query_sql + note_condition_sql + 'order by comment_time desc limit 3',
                    [*note_params], camel=False)
                # print(note_list)
                similar_item = {'timeAt': convert_to_relative_time(similar_update_time), 'alarmId': similar_id,
                                'lastCommenter': '', 'lastHandler': similar_handler, 'result': ''}
                if note_list:
                    similar_item['lastCommenter'] = note_list[0].get('operator', '')
                    similar_item['result'] = '|#|'.join([noteitem['comment_text'] for noteitem in note_list])

        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': similar_item,
                    'similarIds': similarIds,
                    'count': 1}

        return Response(res_dict, http_status.HTTP_200_OK)


class AlarmExistsResourceView(APIView):
    "告警相似存活"

    @try_catch
    def post(self, request):
        data = request.data
        logger.debug(data)
        labels = data.get("labels", '')
        identityKv = data.get("identityKv", {})
        identityId = data.get("identityId", 1)
        # sql origin
        page_size = int(data.get("size", 10))
        page_no = int(data.get("page", 1))
        user_query_sql = 'select a.identity_tag_kv,a.id,a.times,status from alarm_identity a '
        obj_id_query_sql = 'select a.id from alarm_identity a '
        condition_sql = f' where a.status!=0 and a.id!={identityId}'
        params = []
        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [], 'count': 0}
        if labels and identityId:
            for label in labels.split(','):
                label_val = identityKv.get(label, '')
                condition_sql += f" and (JSON_EXTRACT(identity_tag_kv,'$.{label}')=%s ) "
                params.extend([label_val])
        else:
            resp['status'] = 'fail'
            resp['message'] = 'labels and identityId null'
            return Response(resp, http_status.HTTP_200_OK)
        total_cnt = dict_query(
            "select count(1) cnt from ( " + obj_id_query_sql + condition_sql +
            " ) a ", params)[0]['cnt']

        if total_cnt == 0:
            return Response(resp, http_status.HTTP_200_OK)

        resp_list = dict_query(
            user_query_sql + condition_sql +
            ' order by ' + 'updated_at desc' + ' limit %s,%s',
            [*params, (page_no - 1) * page_size, page_size], camel=False)
        for item in resp_list:
            identity_tag_kv = json.loads(item.pop('identity_tag_kv'))
            item['identity_tag_kv'] = identity_tag_kv

        resp['data'] = resp_list
        resp['count'] = total_cnt
        resp['message'] = 'successful'
        return Response(resp, http_status.HTTP_200_OK)


class AlarmBatchCommentResoureView(APIView):

    @try_catch
    def post(self, request):
        data = request.data
        resp = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': f'OK'}
        login_user = request.realname if hasattr(request, "realname") else "system"
        postIds = data.get('postIds', [])
        comment_text = data.get("comment_text", "")
        comment_content = {
            "comment_text": comment_text,
            "comment_type": "text",
        }
        ls_create = []
        for x in postIds:
            dict_ = {
                'identity_id': x,
                'comment_content': comment_content,
                'operator': login_user,
            }
            ls_create.append(AlarmComment(**dict_))

        if ls_create:
            AlarmComment.objects.bulk_create(ls_create)

        resp['data'] = {}

        return Response(resp, http_status.HTTP_200_OK)


class AlarmLocateView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        request_data['size'] = 100
        request_data['removeTime'] = True
        request_data['timeSorter'] = 'ascend'
        # timeSorter = request_data.get('timeSorter','descend')
        logger.info("request_data:%s", request_data)
        scrollTypeOrigin = request_data.get('scrollType', 'both')
        if scrollTypeOrigin == 'both':
            scrollTypeList = ['prev', 'next']
        else:
            scrollTypeList = [scrollTypeOrigin]
        res_all_dict = {}
        for scrollType in scrollTypeList:
            request_data['scrollType'] = scrollType
            post_data = copy.deepcopy(request_data)
            resp_data, time_field = alarm_query_deploy_data(post_data, excludes=False)
            res_dict['count'] = resp_data.get('total', 0)
            resp_pro_list = []
            for item in resp_data['data']:
                event_dict = item['_source']
                time_str = event_dict[time_field]

                msg = f'[{time_str}] [{event_dict.get("status", "")}] [{event_dict.get("execution", "")}] [{event_dict.get("severity", "")}] [指纹ID:{event_dict.get("alarm_id", "")}] [告警ID:{event_dict.get("srmid", "")}] [{event_dict.get("source", "")}|{event_dict.get("group", "")}|{event_dict.get("job", "")}|{event_dict.get("alertname", "")}|{event_dict.get("instance", "")}] 【{event_dict.get("alarm_summary", "")}】-{event_dict.get("alarm_desc", "")}'
                resp_pro_list.append(
                    {
                        "content": msg,
                        "search_after": item.get('sort', []),
                        "_id": {item.get("_id")},
                    })
            if scrollType == 'prev':
                # 不用reverse 前端好处理
                resp_pro_list.reverse()
                res_all_dict['prev'] = resp_pro_list
            else:
                res_all_dict['next'] = resp_pro_list
        # if timeSorter=='descend':
        #     res_all_dict['prev'],res_all_dict['next'] = res_all_dict['next'],res_all_dict['prev']
        res_dict['data'] = res_all_dict

        return Response(res_dict, http_status.HTTP_200_OK)
