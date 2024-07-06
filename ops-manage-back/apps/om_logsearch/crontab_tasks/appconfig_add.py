# -*- coding: utf-8 -*-
import requests, json
import os
from datetime import datetime
import subprocess as sp
import time
from elasticsearch import Elasticsearch

OPS_TOKEN = os.environ.get('OPS_TOKEN', 'kn6xCoKsNkdMvwDOwmyiYgsyL6y7')
headers = {'content-type': 'application/json', "ApiToken": OPS_TOKEN}
# test
OPS_DOMAIN = os.environ.get('OPS_DOMAIN', 'http://127.0.0.1:8000')

# prod
# OPS_DOMAIN = os.environ.get('OPS_DOMAIN','http://10.110.1.17:8000')

posturl = f"{OPS_DOMAIN}/ops-manage/v1/api/log/appconfig"


def list_split(all_list, group_num=100):
    all_num = len(all_list)
    singel_s = all_num // group_num
    ll_new = []
    for i in range(singel_s + 1):
        ls_1 = all_list[i * group_num:(i + 1) * group_num]
        ll_new.append(ls_1)
    return ll_new


def gethosts():
    url_hosts = f'{OPS_DOMAIN}/ops-manage/v1/api/log/source'
    resp = requests.get(url_hosts, headers=headers)
    res_data = []
    try:
        data = resp.json().get('data')
        res_data = data
    except:
        print('return data is null')
    return res_data
def get_index_config(datasource_id,field_type):
    url_hosts = f'{OPS_DOMAIN}/ops-manage/v1/api/log/component'
    resp = requests.get(url_hosts, headers=headers,params={
        'field_type':field_type,
        'source':'es',
        'datasource_id':datasource_id,
    })
    res_data = []
    try:
        data = resp.json().get('data')
        res_data = data
    except:
        print('return data is null')
    return res_data




class EsOperation:
    def __init__(self, es_host="127.0.0.1:9200", es_username="", es_password=""):
        es_host_list = []
        for item in es_host.split(','):
            if not 'http' in item:
                es_host_list.append('http://' + item)
        self.es_username = es_username if es_username else ''
        self.es_password = es_password if es_password else ''
        self.es = Elasticsearch(es_host_list, http_auth=(self.es_username, self.es_password), timeout=3600
                                )

    def map_fun_origin(self, data):
        map_data = data["_source"]
        return map_data

    def agg_body(self, data):
        startTime = strtime2int(data['fromTime'])
        endTime = strtime2int(data['toTime'])
        time_field = data.get("time_field", '')
        if not time_field:
            raise Exception('time_field null')
        querybody = data.get("query", {})
        query = {}

        query["bool"] = {}
        query["bool"]["must"] = []
        if startTime > 0 and endTime > 0:
            timestamp = {
                "range": {
                    time_field: {
                        "gte": startTime,
                        "lt": endTime,
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif startTime > 0:
            timestamp = {
                "range": {
                    time_field: {
                        "gte": startTime
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif endTime > 0:
            timestamp = {"range": {time_field: {"lt": endTime}}}
            query["bool"]["must"].append(timestamp)
        if querybody:
            for key, val in querybody.items():
                if key == 'bool' and isinstance(val, dict):
                    for inner_key, inner_val in val.items():
                        if inner_key == 'must':
                            querybody['bool']['must'].extend(query["bool"]["must"])
            res_query = querybody
        else:
            res_query = query
        return res_query

    def es_alarmapi(self, request_data):
        is_origin = request_data.get('is_origin', False)
        if not is_origin:
            index_str = request_data.get('index_str', '')
            aggs = request_data.get('aggs', '')
            size = request_data.get('size', '')
            _source = request_data.get('_source', '')

            if index_str:
                search_index = index_str
            else:
                raise Exception('component null')
            body = self.agg_body(request_data)
            body_pro = {
                "size": size,
                "_source": _source,
                "timeout": "180s",
                "query": body,
            }
            if aggs:
                body_pro['aggs'] = aggs
            if not _source:
                body_pro.pop('_source')

            param_dict = {
                'body': body_pro,
                'index': search_index,
            }
        else:
            param_dict = request_data.get('param_dict', {})
        # print(param_dict)
        query_data = self.es.search(**param_dict)
        es_datas = list(map(self.map_fun_origin, query_data["hits"]["hits"]))
        res_data = {'data': es_datas,
                    'aggregations': query_data.get('aggregations') if query_data.get('aggregations') else {}}
        return res_data

def strtime2int(time_str,format='%Y-%m-%dT%H:%M:%S'):
    time_int = int(time.mktime(time.strptime(time_str.split('.')[0], format)) * 1000)
    return time_int
def es_search_domain(source_dict):
    
    host = source_dict.get('host')
    datasource_id = source_dict.get('id')
    es_index_config = get_index_config(datasource_id,'applog')
    component_dict = {}
    for item in es_index_config:
        component_dict[item['component']] = {
            'index_str': item['index_str'],
            'time_field': item['time_field'],
        }
    if host:
        username = source_dict.get('username')
        password = source_dict.get('password')

        es = EsOperation(host, username,password)

        for component,dict_com in component_dict.items():
            data = {
                "index_str":dict_com['index_str'],
                "time_field":dict_com['time_field'],
                "fromTime": START_TIME,
                "toTime": END_TIME,
                "size": 0,
                "aggs": {
                    "resp":
                        {"terms":
                             {
                              "field": "clusterid.keyword",
                              "size": 9999
                              }
                         }
                }
            }
            data['fromTimeint'] = strtime2int(data['fromTime'])
            data['toTimeint'] = strtime2int(data['toTime'])
            es_resp = es.es_alarmapi(data)
            aggregations = es_resp['aggregations']
            print('es_resp>>>',component,es_resp)
            for bucket in aggregations.get('resp',{}).get('buckets',[]):
                domain = bucket.get('key','')
                if domain:
                    insert_dict = {
                        'app':domain,
                        'component':component,
                        'datasource_id':datasource_id,
                    }
                    print('_'*30)
                    print(insert_dict)
                    response = requests.request("PUT", posturl, headers=headers, data=json.dumps(insert_dict))
                    print('opsmangeresp>>>',response.text)


def upload():
    datasource_list = gethosts()
    verify_str = ''
    for source_dict in datasource_list:
        ls_post = []

        source = source_dict.get('source')
        if source == 'es':
            es_search_domain(source_dict)

def get_timestamp(time_input):
    timeArray = time.strptime(time_input, "%Y-%m-%dT%H:%M:%S")
    timeStamp = int(time.mktime(timeArray) * 1000)
    return timeStamp
if __name__ == '__main__':


    END_TIME = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
    # 时间间隔计算,最近3h
    DELTA_TIME = 3*60
    time_end = get_timestamp(END_TIME)
    START_TIME = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime((time_end - DELTA_TIME * 60000) / 1000))
    time_start = get_timestamp(START_TIME)
    print(START_TIME, END_TIME)
    print('start add appconfig.......................')
    print(datetime.now())
    upload()
    print('end add appconfig.......................')
    print(datetime.now())
