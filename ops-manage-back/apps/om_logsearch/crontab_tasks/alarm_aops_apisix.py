# -*- coding: utf-8 -*-
import copy

import requests, json
import os
from datetime import datetime
import time

OPS_TOKEN = os.environ.get('OPS_TOKEN', 'kn6xCoKsNkdMvwDOwmyiYgsyL6y7')
headers = {'content-type': 'application/json', "ApiToken": OPS_TOKEN}
# test
# OPS_DOMAIN = os.environ.get('OPS_DOMAIN', 'http://127.0.0.1:8000')

# prod
OPS_DOMAIN = os.environ.get('OPS_DOMAIN', 'http://172.30.13.37:4346')
def send_webhook(send_data):
    print(send_data)
    alarm_labels = {
        "id": 602,
        "severity": "一般",
        "alertname": "网关日志检查异常",
        "job": "alarm_aops-apisix_check",
        "group": "日志检查",
        "instance": "10.110.1.17",
        "source": "网关日志crontab"
    }
    alertname = alarm_labels['alertname']
    summary = '网关日志检查异常'
    # try:
    #     url = 'http://172.30.13.37:9528/ops-manage/v1/api/alarm/alert'
    #     request_data = {
    #         "labels": alarm_labels,
    #         "annotations": {
    #             "summary": summary,
    #             "description": send_data
    #         }
    #     }
    #     resp = requests.post(url, json=request_data, timeout=3)
    #     print(resp.text)
    # except Exception as e:
    #     print(f'send_ops_alarm err:{e}')

    # alarm_labels['id'] = 602



def gethosts():
    url_hosts = f'{OPS_DOMAIN}/ops-manage/v1/api/log/source'
    resp = http_op(url_hosts, method='get', data={})
    res_data = resp.get('data', [])
    return res_data


def http_op(url_hosts, data, method="post"):
    resp_data = {}
    if method == 'post':
        resp = requests.post(url_hosts, headers=headers, data=json.dumps(data))
        resp_data = resp.json()
    elif method == 'get':
        resp = requests.get(url_hosts, headers=headers, params=data)
        resp_data = resp.json()
    return resp_data


def reqeust_err_monitor(data_query_origin, domain, content_nginx):
    data_query = copy.deepcopy(data_query_origin)
    if data_query["query"]["bool"].get('must_not', []):
        has_filter = True
    else:
        has_filter = False
    component = data_query['component']
    data_query['aggs'] = {
        "count": {
            "value_count": {
                "field": "_id"
            }
        },
        "errorCount": {
            "filter": {
                "bool": {"must": [
                    {"match": {"status": "500,501,502,503,504"}},
                ]}
            }
        },
    }
    # print(data_query)
    url_hosts = f'{OPS_DOMAIN}/ops-manage/v1/api/log/datasearch'
    mess_json = http_op(url_hosts, data={'post_data': data_query})
    aggregations = mess_json.get('data',{}).get('aggregations', {})

    totalCnt = aggregations.get('count', {}).get('value', 0)
    errCnt = aggregations.get('errorCount', {}).get('doc_count', 0)
    if totalCnt == 0:
        errRatio = 0
    else:
        errRatio = round((errCnt / totalCnt) * 100, 2)
    print(f'es_resp>>>errCnt:{errCnt},errRatio:{errRatio},totalCnt:{totalCnt}')

    if errCnt >= GT500_MAX and (errRatio >= ERR_RATE_SLA):
        link = OPS_DOMAIN + f'/#/gatelogs?component={component}&domain={domain}&startTime={START_TIME}&endTime={END_TIME}&status=500,501,502,503,504'
        if has_filter:
            link += '&filterflag=1'
        errlink = f'【[日志链接]({link})】'
        content_nginx.append("%s组件%s域名于%s-%s出现50x日志【条数%s】错误率【%s】总量【%s】%s" % (
            component, domain, START_TIME, END_TIME, errCnt, errRatio, totalCnt, errlink))
    return content_nginx


def request_time_monitor(data_query_origin, domain, content_nginx):
    data_query = copy.deepcopy(data_query_origin)
    if data_query["query"]["bool"].get('must_not', []):
        has_filter = True
    else:
        has_filter = False
    component = data_query['component']
    data_query['aggs'] = {
        "results": {
            "terms": {
                "field": "uri.keyword",
                "size": 9999
            },
            "aggs": {
                "errorCount": {
                    "filter": {
                        "range": {
                            "request_time": {
                                "gt": RES_TIME_MAX
                            }
                        }
                    }

                }

            }
        }

    }
    # print(data_query)
    path_cnt_list = []
    overTimeCnt = 0
    overtimeDetail = ''
    url_hosts = f'{OPS_DOMAIN}/ops-manage/v1/api/log/datasearch'
    mess_json = http_op(url_hosts, data={'post_data': data_query})

    results = mess_json.get('data', {}).get('aggregations',{}).get('results',{})

    buckets = results.get('buckets', [])
    for item in buckets:
        #超时率 item['errorCount']['doc_count']/item['doc_count']
        if int(item['errorCount']['doc_count'])>0:
            path_cnt_list.append({'path': item['key'], 'cnt': item['errorCount']['doc_count']})

    if path_cnt_list:
        overtimeDetail = path_cnt_list
        overTimeCnt = sum(map(lambda x: int(x['cnt']), path_cnt_list))
    print(f'overtime_es_resp>>>errCnt:{overTimeCnt}')
    if overTimeCnt > GT_RES_TIME_NUM:
        link = OPS_DOMAIN + f'/#/gatelogs?component={component}&domain={domain}&startTime={START_TIME}&endTime={END_TIME}&request_time=>{RES_TIME_MAX}'
        if has_filter:
            link += '&filterflag=1'
        errlink = f'【[日志链接]({link})】'
        content_nginx.append("%s组件%s域名于%s-%s出现超时日志(大于%sS)【条数%s】,超时接口【%s】%s" % (
        component,domain, START_TIME, END_TIME, RES_TIME_MAX, overTimeCnt, overtimeDetail,errlink))
    return content_nginx


def es_search_domain():
    # 只监控 yewu-apisix组件的网关日志
    component_dict = {
        'aops-apisix': {'data': [
            {
                'domain': 'ebg.appcloud.iflytek.com'
            }
        ]}
    }
    for component, dict_com in component_dict.items():
        # 监控组件下所有域名状态
        # resp_data = http_op(f'{OPS_DOMAIN}/ops-manage/v1/api/log/gatelist',method='get', data={
        #     'component':component,
        # })
        resp_data = dict_com
        for domain_dict in resp_data.get('data', []):
            domain = domain_dict.get('domain')
            # 调接口模式-
            content_nginx = []

            data_query = {
                "component": component,
                "fromTime": START_TIME,
                "toTime": END_TIME,
                "size": 0,
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"http_host": domain}}
                        ]
                    }
                }

            }
            exclude_uri_data = http_op(f'{OPS_DOMAIN}/ops-manage/v1/api/log/gatefilter', method='get', data={
                'domain': domain,
                'component': component,
            })
            # print('exclude_uri_data>>>', exclude_uri_data)
            exclude_uri_data_list = exclude_uri_data.get('data', [])
            for item in exclude_uri_data_list:
                item = item.replace(':', '\\:').replace("'", "\\'").replace("(", "\\(").replace(")", "\\)").replace('"',
                                                                                                                    '\\"').replace(
                    '.', '\\.').replace('/', '\\/')
            if exclude_uri_data_list:
                # 加过滤接口
                data_query["query"]["bool"]["must_not"] = [{"match_phrase": {"uri": i}} for i in exclude_uri_data_list]
            # 域名下响应时间监控
            content_nginx = reqeust_err_monitor(data_query, domain, content_nginx)
            content_nginx = request_time_monitor(data_query, domain, content_nginx)
            if content_nginx:
                send_webhook(content_nginx)

def upload():
    # datasource_list = gethosts()
    # for source_dict in datasource_list:
    #     source = source_dict.get('source')
    #     if source == 'es':
    #         es_search_domain(source_dict)
    es_search_domain()


def get_timestamp(time_input):
    timeArray = time.strptime(time_input, "%Y-%m-%dT%H:%M:%S")
    timeStamp = int(time.mktime(timeArray) * 1000)
    return timeStamp


if __name__ == '__main__':
    END_TIME = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
    # 时间间隔计算,最近10min
    DELTA_TIME = 10
    time_end = get_timestamp(END_TIME)
    START_TIME = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime((time_end - DELTA_TIME * 60000) / 1000))
    time_start = get_timestamp(START_TIME)

    # 出现500的数量>GT500_MAX && 错误率>=ERR_RATE_SLA% 报警
    GT500_MAX = 1
    ERR_RATE_SLA = 0.5

    # #响应时间>RES_TIME_MAXs 超过GT_RES_TIME_NUM条告警
    RES_TIME_MAX = 3.5
    GT_RES_TIME_NUM = 3

    print(START_TIME, END_TIME)
    print('start monitor gate.......................')
    print(datetime.now())
    upload()
    print('end monitor gate.......................')
    print(datetime.now())
