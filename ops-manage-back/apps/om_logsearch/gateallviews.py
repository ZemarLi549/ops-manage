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


def common_deploy_data(post_data, aggs, respKey='buckets'):
    datasource_id = post_data.get('datasource_id')
    component = post_data.get('component')
    if component and '|' in component:
        compo_ls = component.split('|')
        component = compo_ls[1]
        datasource_id = int(compo_ls[0])
    domain = post_data.get('domain')
    datasourceDict = getDatasourceInfo(datasource_id, component, domain, '')
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
            aggs_str = json.dumps(aggs)
            if '$timestamp$' in aggs_str:
                aggs = json.loads(aggs_str.replace('$timestamp$', componentObj.get('time_field')))

        # 预处理数据
        post_data = es.es_gateall_deploy(post_data, aggs=aggs)
        es_resp = es.es_alarmapi(post_data)
        resp_data = es_resp['aggregations'].get('resp', {}).get(respKey, [])
    else:
        resp_data = []
    return resp_data


class AllHostTableView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        logger.info("request_data:%s", request_data)
        aggs = {
            "resp":
                {
                    "terms":
                        {
                            "field": "uri.keyword",
                            "size": 9999
                        },
                    "aggs": {
                        "errorCount": {
                            "filter": {
                                "bool": {"must": [
                                    {"match": {"status": "500,501,502,503,504"}},
                                    # {"match": {"status.value": "500,501,502,503,504"}},
                                ]}
                            }
                        },
                        "maxResp": {"max": {"field": "request_time"}},
                        "net_out": {"sum": {"field": "bytes_sent"}},
                        "net_in": {"sum": {"field": "request_length"}},
                        "request_time_outlier": {
                            "percentiles": {
                                "field": "request_time",
                                "percents": [50, 90]
                            }
                        },
                        # "uv": {
                        #     "cardinality": {
                        #         # {"script":
                        #         #     {
                        #         #         "source": "doc['http_x_forwarded_for.keyword'].value.split(',')[0]",
                        #         #         "lang": "painless",
                        #         #
                        #         #     },
                        #         #     "size": 9999
                        #         # }
                        #         "field": "http_x_forwarded_for.keyword"
                        #     }
                        # }
                    }
                }
        }
        resp_data = common_deploy_data(request_data, aggs)
        resp_data_pro = []
        maxresp = 0
        totalCnt = 0
        errCnt = 0

        for item in resp_data:
            dict_ = {}
            dict_['path'] = item.get('key')
            dict_['totalCount'] = item.get('doc_count')
            # dict_['uv'] = item.get('uv')['value']
            try:
                dict_['errorCount'] = item.get('errorCount')['buckets'][0]['doc_count']
            except:
                dict_['errorCount'] = 0
            dict_['errorRatio'] = myround(dict_['errorCount'] * 100 / dict_['totalCount'], 3)
            dict_['fiveResp'] = myround((item.get('request_time_outlier')['values']['50.0']), 3)
            dict_['nineResp'] = myround((item.get('request_time_outlier')['values']['90.0']), 3)
            dict_['maxResp'] = myround((item.get('maxResp')['value']), 3)
            dict_['net_out'] = myround((item.get('net_out')['value']) / 1048576, 3)
            dict_['net_in'] = myround((item.get('net_in')['value']) / 1048576, 3)
            if maxresp <= dict_['maxResp']:
                maxresp = dict_['maxResp']
            totalCnt += dict_['totalCount']
            resp_data_pro.append(dict_)
        # 附加数据
        df = pd.DataFrame(list(resp_data_pro))
        resp_ = {}
        try:
            resp_['fiveresp'] = round(df['fiveResp'].quantile(q=0.5), 3)
            resp_['nineresp'] = round(df['nineResp'].quantile(q=0.9), 3)
        except Exception as e:
            resp_['fiveresp'] = 0
            resp_['nineresp'] = 0
        resp_['maxresp'] = maxresp
        resp_['totalCnt'] = totalCnt
        resp_['errCnt'] = errCnt
        try:
            resp_['errRate'] = round((errCnt / totalCnt) * 100, 3)
        except:
            resp_['errRate'] = 0
        res_dict['data'] = resp_data_pro
        res_dict['count'] = len(resp_data_pro)
        res_dict['appendData'] = resp_
        return Response(res_dict, http_status.HTTP_200_OK)


class StatusLineView(APIView):
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
                },
                "aggs": {
                    "lineresp":
                        {"terms":
                            {"script":
                                {
                                    "source": "doc['status.keyword'].value.substring(0, 1) + 'xx'"
                                    # "source": "doc['status'].value.toString().substring(0, 1) + 'xx'"

                                },
                            }

                        }
                }
            }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs)
        resp_data_pro = []
        for item in resp_data:
            timestr = format_time(item['key_as_string'], formatstr)
            lineresp_buck = item['lineresp']['buckets']
            for mc_item in lineresp_buck:
                dict_ = {}
                dict_['timestr'] = timestr
                dict_['name'] = mc_item['key']
                dict_['cnt'] = mc_item['doc_count']
                resp_data_pro.append(dict_)

        xList, resp_data_pro = pd_return(resp_data_pro, 'timestr', 'name', 'cnt')
        res_dict['dataList'] = resp_data_pro
        res_dict['xList'] = xList

        return Response(res_dict, http_status.HTTP_200_OK)


class ReqAllLineView(APIView):
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
                },
                "aggs": {
                    "maxResp": {"max": {"field": "request_time"}},
                    "request_time_outlier": {
                        "percentiles": {
                            "field": "request_time",
                            "percents": [50, 90]
                        }
                    }
                }
            }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs)
        maxList = []
        per50List = []
        per90List = []
        xList = []
        for item in resp_data:
            xList.append(format_time(item.get('key_as_string'), formatstr))
            maxList.append(myround(item.get('maxResp')['value'], 3))
            per90List.append(myround(item.get('request_time_outlier')['values']['90.0'], 3))
            per50List.append(myround(item.get('request_time_outlier')['values']['50.0'], 3))
        dict_max = {'name': 'maxresp', 'yList': maxList}
        dict_per50 = {'name': 'per50', 'yList': per50List}
        dict_per90 = {'name': 'per90', 'yList': per90List}
        resp_data_pro = [dict_max, dict_per50, dict_per90]

        res_dict['dataList'] = resp_data_pro
        res_dict['xList'] = xList

        return Response(res_dict, http_status.HTTP_200_OK)


class NetAllLineView(APIView):
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
                },
                "aggs": {
                    "netout": {"sum": {"field": "bytes_sent"}},
                    "netin": {"sum": {"field": "request_length"}}
                }
            }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs)
        maxList = []
        avgList = []
        xList = []
        for item in resp_data:
            xList.append(format_time(item.get('key_as_string'), formatstr))
            maxList.append(
                myround((item.get('netin')['value']) / 1048576, 3) if item.get('netin')['value'] != 'null' else 0)
            avgList.append(
                myround((item.get('netout')['value']) / 1048576, 3) if item.get('netout')['value'] != 'null' else 0)
        dict_max = {'name': 'netin', 'yList': maxList}
        dict_avg = {'name': 'netout', 'yList': avgList}
        resp_data_pro = [dict_max, dict_avg]

        res_dict['dataList'] = resp_data_pro
        res_dict['xList'] = xList

        return Response(res_dict, http_status.HTTP_200_OK)


class MethodStatusLineView(APIView):
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
                },
                "aggs": {
                    "lineresp":
                        {"terms":
                            {"script":
                                {
                                    "lang": "painless",
                                    "source": "doc['status.keyword'].value.substring(0, 1) + 'xx' + '_' + doc['request_method.keyword'].value"
                                    # "source": "doc['status'].value.toString().substring(0, 1) + 'xx' + '_' + doc['request_method.keyword'].value"
                                },
                            }

                        }
                }
            }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs)
        resp_data_pro = []
        for item in resp_data:
            timestr = format_time(item['key_as_string'], formatstr)
            lineresp_buck = item['lineresp']['buckets']
            for mc_item in lineresp_buck:
                dict_ = {}
                dict_['timestr'] = timestr
                dict_['name'] = mc_item['key']
                dict_['cnt'] = mc_item['doc_count']
                resp_data_pro.append(dict_)

        xList, resp_data_pro = pd_return(resp_data_pro, 'timestr', 'name', 'cnt')
        res_dict['dataList'] = resp_data_pro
        res_dict['xList'] = xList

        return Response(res_dict, http_status.HTTP_200_OK)


class RespPieView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        aggs = {
            "resp":
                {"terms":
                     {"script":
                          {
                              "source": "def request_time=doc['request_time'].value;def reqeust_str = '<0.1s';if(request_time<0.1){reqeust_str='<0.1s'}else if(request_time<0.5){reqeust_str='<0.5s'}else if(request_time<1){reqeust_str='<1s'}else if(request_time<2){reqeust_str='1-2s'}else if(request_time<5){reqeust_str='2-5s'}else if(request_time<2){reqeust_str='1-2s'}else if(request_time<10){reqeust_str='5-10s'}else if(request_time<10){reqeust_str='10-15s'}else{reqeust_str='>15s'}return reqeust_str"},
                      "size": 9999
                      }
                 }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs)
        resp_data_pro = []
        for item in resp_data:
            dict_ = {}
            dict_['name'] = item.get('key')
            dict_['value'] = int(item.get('doc_count')) if item.get('doc_count') != 'null' else 0
            resp_data_pro.append(dict_)
        res_dict['dataList'] = resp_data_pro
        return Response(res_dict, http_status.HTTP_200_OK)


class ClientPieView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        aggs = {
            "resp":
                {"terms":

                     {"field": 'http_x_forwarded_for.keyword',
                      "size": 9999
                      }
                 #        {"script":
                 #            {
                 #                "source":"""
                 #   def ips = doc['http_x_forwarded_for.keyword'].value;
                 #    if (ips != null && ips.length() > 0) {
                 #     return ips.split(',')[0].trim();
                 #   }
                 #   return 'unknown';
                 # """,
                 #                "lang": "painless",
                 #
                 #            },
                 #         "size":9999
                 #        }
                 }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs)
        resp_data_pro = []
        res_data_dict = {}
        for item in resp_data:
            key_ = item.get('key')
            value_ = int(item.get('doc_count')) if item.get('doc_count') != 'null' else 0
            key_ = key_.split(',')[0]
            if not key_ in res_data_dict.keys():
                res_data_dict[key_] = value_
            else:
                res_data_dict[key_] += value_
        for key, val in res_data_dict.items():
            resp_data_pro.append({
                'name': key,
                'value': val,
            })
        res_dict['dataList'] = resp_data_pro
        return Response(res_dict, http_status.HTTP_200_OK)


class CommonPieView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        fieldKey = request_data.get('fieldKey', 'request_method')
        aggs = {
            "resp":
                {"terms":
                     {
                      "field": fieldKey + '.keyword',
                      # "field": fieldKey + '.keyword'  if not fieldKey=='status' else fieldKey,
                      "size": 9999
                      }
                 }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs)
        resp_data_pro = []
        for item in resp_data:
            dict_ = {}
            dict_['name'] = item.get('key')
            dict_['value'] = int(item.get('doc_count')) if item.get('doc_count') != 'null' else 0
            resp_data_pro.append(dict_)
        res_dict['dataList'] = resp_data_pro
        return Response(res_dict, http_status.HTTP_200_OK)


class FiveNineRespView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        aggs = {
            "resp": {
                "percentiles": {
                    "field": "request_time",
                    "percents": [50, 90]
                }
            }
        }
        logger.info("request_data:%s", request_data)
        resp_data = common_deploy_data(request_data, aggs, respKey='values')

        res_dict['dataDict'] = {
            'fiveresp': myround(resp_data.get('50.0'), 3),
            'nineresp': myround(resp_data.get('90.0'), 3),
        }

        return Response(res_dict, http_status.HTTP_200_OK)


def query_deploy_data(post_data):
    resp_data = {}
    time_field = '@timestamp'
    datasource_id = post_data.get('datasource_id')
    component = post_data.get('component')

    if component and '|' in component:
        compo_ls = component.split('|')
        component = compo_ls[1]
        datasource_id = int(compo_ls[0])
    domain = post_data.get('domain')
    datasourceDict = getDatasourceInfo(datasource_id, component, domain, '')
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

        # 预处理数据
        timeSorter = post_data.get('timeSorter', 'descend')
        # prev 上一页 上拉获取一页数据，配合search_after,结果所有条件逆序下
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
        post_data = es.es_gateall_deploy(post_data)
        resp_data = es.es_alarmapi(post_data, allHits=True)
    return resp_data, time_field


class GateQueryView(APIView):
    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        logger.info("request_data:%s", request_data)
        historyPage = request_data.get('page', 1)
        scrollType = request_data.get('scrollType', 'next')
        resp_data, time_field = query_deploy_data(request_data)
        res_dict['count'] = resp_data.get('total', 0)
        resp_pro_list = []
        for item in resp_data['data']:
            event_dict = item['_source']['event']['original']
            event_dict = json.loads(event_dict)
            message = event_dict.get('message', '{}')
            message = json.loads(message)
            message['time_str'] = ms_format_time(event_dict[time_field])
            message['host_name'] = event_dict.get('host', {}).get('name', '')
            message['log_path'] = event_dict.get('log', {}).get('file', {}).get('path', '')
            dict_ = {
                '_id': item.get('_id', ''),
                'search_after': item.get('sort', []),
                'message': message,
            }
            resp_pro_list.append(dict_)
        if scrollType == 'prev':
            resp_pro_list.reverse()
        res_dict['data'] = resp_pro_list
        res_dict['historyPage'] = historyPage

        return Response(res_dict, http_status.HTTP_200_OK)
