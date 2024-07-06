import copy
import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from apps.common.renderers import MyJSONRenderer
from .serializers import *
from .esQuery import EsOperation
from django.conf import settings
from apps.common.try_catch import try_catch, power_decorator
from .models import *
import json
from apps.common.tools import Execution
from apps.common.tools import encrypt
from apps.common.dbopr import dict_query
from apps.common.utils import count_kuadu, format_time, pd_return, ms_format_time
from apps.common.redisclient import getDatasourceInfo, getComponentInfo
from apps.common.dbopr import get_func, put_func, delete_func, to_underline, get_relative_func
import logging
import pandas as pd

logger = logging.getLogger(__name__)


# from drf_yasg import openapi

# Create your views here.
def myround(data, int_num):
    try:
        resp = round(data, int_num)
        return resp
    except:
        return 0


def app_common_deploy_data(post_data, aggs, respKey='buckets'):
    datasource_id = post_data.get('datasource_id')
    component = post_data.get('component')
    if component and '|' in component:
        compo_ls = component.split('|')
        component = compo_ls[1]
        datasource_id = int(compo_ls[0])
    app = post_data.get('app')
    datasourceDict = getDatasourceInfo(datasource_id, component, '', app)
    source_type = datasourceDict['source']
    es_host = datasourceDict['host']
    es_username = datasourceDict['username']
    es_pwd = datasourceDict['password']
    if source_type == 'es' and es_host:
        es = EsOperation(es_host, es_username, es_pwd)
        if component:
            componentObj = getComponentInfo(component, 'es')
            post_data['index_str'] = componentObj.get('index_str')
            post_data['time_field'] = componentObj.get('time_field')
            if app:
                post_data['index_str'] = post_data['index_str'].replace('*', f'{app}*')
            aggs_str = json.dumps(aggs)
            if '$timestamp$' in aggs_str:
                aggs = json.loads(aggs_str.replace('$timestamp$', componentObj.get('time_field')))

        # 预处理数据
        post_data = es.es_app_deploy(post_data, aggs=aggs)
        es_resp = es.es_alarmapi(post_data)
        resp_data = es_resp['aggregations'].get('resp', {}).get(respKey, [])
    else:
        resp_data = []
    return resp_data


class HistoryGramAggView(APIView):
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
        resp_data = app_common_deploy_data(request_data, aggs)
        resp_data_pro = []
        for item in resp_data:
            timestr = format_time(item['key_as_string'], formatstr)
            dict_ = {
                'name': timestr,
                'value': item.get('doc_count', ''),
            }
            resp_data_pro.append(dict_)
        res_dict['data'] = resp_data_pro

        return Response(res_dict, http_status.HTTP_200_OK)


def app_query_deploy_data(post_data):
    resp_data = {}
    time_field = '@timestamp'
    datasource_id = post_data.get('datasource_id')
    component = post_data.get('component')

    if component and '|' in component:
        compo_ls = component.split('|')
        component = compo_ls[1]
        datasource_id = int(compo_ls[0])
    app = post_data.get('app')
    datasourceDict = getDatasourceInfo(datasource_id, component, '', app)
    source_type = datasourceDict['source']
    es_host = datasourceDict['host']
    es_username = datasourceDict['username']
    es_pwd = datasourceDict['password']
    if source_type == 'es' and es_host:
        es = EsOperation(es_host, es_username, es_pwd)
        if component:
            componentObj = getComponentInfo(component, 'es')
            post_data['index_str'] = componentObj.get('index_str')
            post_data['time_field'] = componentObj.get('time_field')
            time_field = post_data['time_field']
            if app:
                post_data['index_str'] = post_data['index_str'].replace('*', f'{app}*')

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
        post_data['_source'] = {
            "includes": [
                "event.original",
            ]
        }
        post_data = es.es_app_deploy(post_data)
        resp_data = es.es_alarmapi(post_data, allHits=True)
    return resp_data, time_field


class AppQueryView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        logger.info("request_data:%s", request_data)
        historyPage = request_data.get('page', 1)
        scrollType = request_data.get('scrollType', 'next')
        resp_data, time_field = app_query_deploy_data(request_data)
        res_dict['count'] = resp_data.get('total', 0)
        resp_pro_list = []
        for item in resp_data['data']:
            event_dict = item['_source']['event']['original']
            event_dict = json.loads(event_dict)
            messageDict = {}
            message = event_dict.get('message', '')

            messageDict['time_str'] = ms_format_time(event_dict[time_field])
            messageDict['host_name'] = event_dict.get('host', {}).get('name', '')
            messageDict['traceId'] = event_dict.get('traceId', '')
            messageDict['level'] = event_dict.get('level', '')
            messageDict['className'] = event_dict.get('className', '')
            messageDict['log_path'] = event_dict.get('log', {}).get('file', {}).get('path', '')
            messageDict['message'] = message
            dict_ = {
                '_id': item.get('_id', ''),
                'search_after': item.get('sort', []),
                'message': messageDict,
            }
            resp_pro_list.append(dict_)
        if scrollType == 'prev':
            resp_pro_list.reverse()
        res_dict['data'] = resp_pro_list
        res_dict['historyPage'] = historyPage

        return Response(res_dict, http_status.HTTP_200_OK)



class AppLocateView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        request_data['removeTime'] = True
        request_data['timeSorter'] = 'ascend'
        # timeSorter = request_data.get('timeSorter','descend')
        logger.info("request_data:%s", request_data)
        scrollTypeOrigin = request_data.get('scrollType', 'both')
        if scrollTypeOrigin=='both':
            scrollTypeList = ['prev','next']
        else:
            scrollTypeList = [scrollTypeOrigin]
        res_all_dict = {}
        for scrollType in scrollTypeList:
            request_data['scrollType'] = scrollType
            post_data = copy.deepcopy(request_data)
            resp_data, time_field = app_query_deploy_data(post_data)
            res_dict['count'] = resp_data.get('total', 0)
            resp_pro_list = []
            for item in resp_data['data']:
                event_dict = item['_source']['event']['original']
                event_dict = json.loads(event_dict)
                message = event_dict.get('message', '')
                time_str = ms_format_time(event_dict[time_field])
                msg = f'[{time_str}]   {message}'
                resp_pro_list.append(
                    {
                    "content":msg,
                    "search_after":item.get('sort', []),
                    "_id":{item.get("_id")},
                })
            if scrollType == 'prev':
                #不用reverse 前端好处理
                resp_pro_list.reverse()
                res_all_dict['prev'] = resp_pro_list
            else:
                res_all_dict['next'] = resp_pro_list
        # if timeSorter=='descend':
        #     res_all_dict['prev'],res_all_dict['next'] = res_all_dict['next'],res_all_dict['prev']
        res_dict['data'] = res_all_dict

        return Response(res_dict, http_status.HTTP_200_OK)