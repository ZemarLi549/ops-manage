import time
import re
from elasticsearch import Elasticsearch
import logging
from apps.common.utils import strtime2int

logger = logging.getLogger(__name__)


class EsOperation:
    def __init__(self, es_host="127.0.0.1:9200", es_username="", es_password=""):
        es_host_list = []
        for item in es_host.split(','):
            if not 'http' in item:
                es_host_list.append('http://' + item)
            else:
                es_host_list.append(item)
        self.es_username = es_username if es_username else ''
        self.es_password = es_password if es_password else ''
        self.es = Elasticsearch(es_host_list, http_auth=(self.es_username, self.es_password), timeout=3600,verify_certs=False)

    def map_fun_origin(self, data):
        map_data = data["_source"]
        return map_data

    def agg_body(self, data):
        fromTime = data.get('fromTime', 0)
        toTime = data.get('toTime', 0)

        if fromTime:
            startTime = strtime2int(data['fromTime'])
        else:
            startTime = 0
        if toTime:
            endTime = strtime2int(data['toTime'])
        else:
            endTime = 0

        time_field = data.get("time_field", '')
        removeTime = data.get("removeTime", False)
        if not time_field:
            raise Exception('time_field null')
        querybody = data.get("query", {})
        query = {}

        query["bool"] = {}
        query["bool"]["must"] = []
        if not removeTime:
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

    def create_filter(self, request_time, es_filed):
        request_time_filter = {}
        if '>' in request_time or '=' in request_time or '<' in request_time:
            request_time_filter = {
                "range": {
                    es_filed: {}
                }
            }
            request_time = request_time.replace(' ', '')
            if '>=' in request_time:
                re_message = re.findall(r">=([0-9.e+-]+)", request_time)
                request_time_filter['range'][es_filed]['gte'] = float(re_message[0])
            elif '>' in request_time:
                re_message = re.findall(r">([0-9.e+-]+)", request_time)
                request_time_filter['range'][es_filed]['gt'] = float(re_message[0])

            if '<=' in request_time:
                re_message = re.findall(r"<=([0-9.e+-]+)", request_time)
                request_time_filter['range'][es_filed]['lte'] = float(re_message[0])
            elif '<' in request_time:
                re_message = re.findall(r"<([0-9.e+-]+)", request_time)
                request_time_filter['range'][es_filed]['lt'] = float(re_message[0])
        return request_time_filter

    def common_gate_query_get(self, post_data):
        query = {}
        query["bool"] = {}
        query["bool"]["must"] = []
        query["bool"]["must_not"] = []
        domain = post_data.get('domain')
        uri = post_data.get('uri')
        args = post_data.get('args')
        client_ip = post_data.get('client_ip')
        status = post_data.get('status')
        request_method = post_data.get('request_method')
        request_time = post_data.get('request_time')
        filterflag = post_data.get('filterflag', False)

        if domain:
            term_ = {"term": {"http_host": domain}}
            query["bool"]["must"].append(term_)
        if uri:
            post_data.pop('uri')
            term_ = {"match": ({"uri": {"query": uri, "operator": "and"}})}
            query["bool"]["must"].append(term_)
        if args:
            post_data.pop('args')
            term_ = {"match": ({"args": {"query": args, "operator": "and"}})}
            query["bool"]["must"].append(term_)
        if client_ip:
            post_data.pop('client_ip')
            term_ = {"match": {"http_x_forwarded_for": client_ip}}
            query["bool"]["must"].append(term_)
        if status:
            post_data.pop('status')
            if isinstance(status, list):
                status = ','.join(status)
            should_dict = {'bool': {'should': []}}
            for item in status.split(','):
                match_ = {"term": {"status": item}}
                should_dict['bool']['should'].append(match_)
            query["bool"]["must"].append(should_dict)

            # match_ = {"match": {"status": status}}
            # query["bool"]["must"].append(match_)

        if request_method:
            post_data.pop('request_method')
            if isinstance(request_method, list):
                request_method = ','.join(request_method)
            match_ = {"match": {"request_method": request_method}}
            query["bool"]["must"].append(match_)
        if request_time:
            post_data.pop('request_time')
            if '>' in request_time or '=' in request_time or '<' in request_time:
                request_time_filter = self.create_filter(request_time, 'request_time')
                if request_time_filter:
                    query["bool"]["must"].append(request_time_filter)
        if filterflag:
            post_data.pop('filterflag')
            allignore = post_data.get('allignore', '')
            # print('allignore>>>',allignore)
            if allignore:
                post_data.pop('allignore')
                query["bool"]["must_not"].extend([{"match_phrase": {"uri": i}} for i in allignore.split('|#|')])
                # regexp 不行
                # query["bool"]["must_not"].append({
                #         "regexp": {
                #             "uri.keyword": f"{allignore.replace('|#|', '|')}"
                #         }
                #     })
        if not query["bool"]["must_not"]:
            query["bool"].pop("must_not")
        return query

    def es_gateall_deploy(self, post_data, aggs=[]):
        page_size = int(post_data.get('size', '100'))
        query = self.common_gate_query_get(post_data)
        post_data['query'] = query
        # 主要是聚合agg
        if aggs:
            post_data['size'] = 0
        else:
            post_data['size'] = page_size
        post_data['aggs'] = aggs
        return post_data
    def es_app_deploy(self, post_data, aggs=[]):
        page_size = int(post_data.get('size', '100'))
        query = self.common_app_query_get(post_data)
        post_data['query'] = query
        # 主要是聚合agg
        if aggs:
            post_data['size'] = 0
        else:
            post_data['size'] = page_size
        post_data['aggs'] = aggs
        return post_data
    def common_app_query_get(self, post_data):
        query = {}
        query["bool"] = {}
        query["bool"]["must"] = []
        query["bool"]["must_not"] = []
        app = post_data.get('app')
        locateType = post_data.get('locateType', 'filter')
        msg = post_data.get('msg')
        queryType = post_data.get('queryType', 'phase')
        log_path = post_data.get('log_path')
        traceId = post_data.get('traceId')
        level = post_data.get('level')
        className = post_data.get('className')
        filterflag = post_data.get('filterflag', False)
        #过滤情况
        if locateType!='normal':
            if msg:
                post_data.pop('msg')
                if queryType == 'phase':
                    term_ = {"match": ({"message": {"query": msg, "operator": "and"}})}
                    query["bool"]["must"].append(term_)
                elif queryType == 'segmen':
                    term_ = {"match": {"message": msg}}
                    query["bool"]["must"].append(term_)
                else:
                    term_ = {"match": {"message": msg}}
                    query["bool"]["must"].append(term_)
            if log_path:
                post_data.pop('log_path')
                term_ = {"match": ({"log_path": {"query": log_path, "operator": "and"}})}
                query["bool"]["must"].append(term_)
            if traceId:
                post_data.pop('traceId')
                term_ = {"match": {"traceId": traceId}}
                query["bool"]["must"].append(term_)
            if className:
                post_data.pop('className')
                term_ = {"match": {"className": className}}
                query["bool"]["must"].append(term_)
            if level:
                post_data.pop('level')
                if isinstance(level, list):
                    level = ','.join(level)
                should_dict = {'bool': {'should': []}}
                for item in level.split(','):
                    match_ = {"term": {"level": item}}
                    should_dict['bool']['should'].append(match_)
                query["bool"]["must"].append(should_dict)
            if filterflag:
                post_data.pop('filterflag')
                allignore = post_data.get('allignore', '')
                if allignore:
                    post_data.pop('allignore')
                    query["bool"]["must_not"].extend([{"match_phrase": {"message": i}} for i in allignore.split('|#|')])

        if app:
            term_ = {"term": {"clusterid.keyword": app}}
            query["bool"]["must"].append(term_)

        if not query["bool"]["must_not"]:
            query["bool"].pop("must_not")
        return query
    def es_alarmapi(self, request_data,allHits=False):
        is_origin = request_data.get('is_origin', False)
        if not is_origin:
            index_str = request_data.get('index_str', '')
            if 'searchTime' in request_data.keys():
                searchTime = request_data['searchTime']
                request_data['fromTime'] = searchTime[0].replace(' ', 'T')
                request_data['toTime'] = searchTime[1].replace(' ', 'T')
            else:
                request_data['fromTime'] = request_data['fromTime'].replace(' ', 'T')
                request_data['toTime'] = request_data['toTime'].replace(' ', 'T')
            aggs = request_data.get('aggs', '')
            size = request_data.get('size', '')
            sort = request_data.get('sort', {})
            _source = request_data.get('_source', '')

            if index_str:
                search_index = index_str
            else:
                raise Exception('component null')
            body = self.agg_body(request_data)
            body_pro = {
                "size": size,
                'track_total_hits': True,
                "_source": _source,
                "timeout": "180s",
                "query": body,
            }
            page_no = int(request_data.get('page', '1'))
            search_after = request_data.get('search_after')
            if search_after:
                body_pro['search_after'] = search_after
            else:
                body_pro['from'] = (page_no - 1) * size

            if sort:
                body_pro['sort'] = sort

            if aggs and size == 0:
                body_pro['aggs'] = aggs
                # 优化，agg不需要精确total
                body_pro['track_total_hits'] = False
            if not _source:
                body_pro.pop('_source')

            param_dict = {
                'body': body_pro,
                'index': search_index,
            }
        else:
            param_dict = request_data.get('param_dict', {})
        print(f'param_dict:{param_dict}')
        query_data = self.es.search(**param_dict)
        if not allHits:
            es_datas = list(map(self.map_fun_origin, query_data["hits"]["hits"]))
        else:
            es_datas =  query_data["hits"]["hits"]
        res_data = {'total': query_data.get('hits', {}).get('total', {}).get('value', 0), 'data': es_datas,
                    'aggregations': query_data.get('aggregations') if query_data.get('aggregations') else {}}
        return res_data
