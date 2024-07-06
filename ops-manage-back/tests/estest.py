from elasticsearch import Elasticsearch
from copy import deepcopy
import re
import logging
import time

logger = logging.getLogger(__name__)

COMPONENT_DICT = {
    'aops-nginx':{'index':'aops-nginx-nginx-*','time_field':'@timestamp'},
    'yewu-tengine':{'index':'aops-tengine-tengine-*','time_field':'@timestamp'},
    'aops-apisix':{'index':'aops-apisix-filelog-*','time_field':'@timestamp'},
    'yewu-apisix':{'index':'aops-apisix-apisix-*','time_field':'@timestamp'},
}
class EsOperation:
    def __init__(self, es_host="10.110.1.11:9113", es_username="", es_password=""):
        es_host_list = []
        for item in es_host.split(','):
            if not 'http' in item:
                es_host_list.append('http://'+item)
        self.es_username = es_username if es_username else ''
        self.es_password = es_password if es_password else ''
        self.es = Elasticsearch(es_host_list, http_auth=(self.es_username, self.es_password), timeout=3600
        )

    def get_instance_list(self, request_data):
        id_ = request_data.get('id', '')
        service, env = id_.split('.')
        startTime = request_data.get("fromTimeint", 0)
        endTime = request_data.get("toTimeint", 0)

        query = {}
        query["bool"] = {}
        query["bool"]["must"] = []
        if env is not None:
            query["bool"]["must"].append({"term": {"env": env}})
        if service:
            query["bool"]["must"].append({"match": {"service": id_}})
        if startTime > 0 and endTime > 0:
            timestamp = {
                "range": {
                    "timestamp": {
                        # "gte": time_format(startTime),
                        "gte": startTime,
                        # "lt": time_format(endTime)
                        "lt": endTime,
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif startTime > 0:
            timestamp = {
                "range": {
                    "timestamp": {
                        # "gte": time_format(startTime)
                        "gte": startTime
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif endTime > 0:
            # timestamp = {"range": {"timestamp": {"lt": time_format(endTime)}}}
            timestamp = {"range": {"timestamp": {"lt": endTime}}}
            query["bool"]["must"].append(timestamp)
        body_pro = {
            "size": 500,
            "from": 0,
            "_source": 'source',
            "timeout": "180s",
            "query": query,
        }
        if service:
            index = "%s_%s_" % (env, service)
        elif env:
            index = env + "_"
        else:
            index = ""

        search_index = "ap_log_" + index + "*"
        param_dict = {
            'typed_keys': '_doc',
            'body': body_pro,
            'index': search_index,
        }
        # logger.info(param_dict)
        query_data = self.es.search(**param_dict)
        es_datas = list(map(self.map_fun_origin, query_data["hits"]["hits"]))
        # logger.info(es_datas[:2])
        resp_data_pro = set()
        for item in es_datas:
            try:
                path = item.get('source').split('/')[-2]
            except:
                path = item.get('source')
            if path:
                resp_data_pro.add(path)
        return list(resp_data_pro)

    def get_search_index(self, data):
        isgate = data.get('isgate')
        service = data.get('service')
        env = data.get('env')
        domain = data.get('domain')

        if service:
            service, env = service.split(".")
            index = "%s_%s_" % (env, service)
        elif env:
            index = env + "_"
        else:
            index = ""

        if isgate == 'y':
            search_index = "ng_log_" + domain + "*"
        else:
            search_index = "ap_log_" + index + "*"
        return search_index

    def es_query(self, data):
        print('*******************')
        print(data)

        query_data = dict()
        scrollId = data.get("scrollId", None)

        search_index = self.get_search_index(data)
        cleanScroll = data.get("cleanScroll", None)
        sort = data.get("sort", None)
        if sort == "descending":
            sort = "desc"
        elif sort == "ascending":
            sort = "asc"

        pageSize = data.get("pageSize", 100)
        pageNo = data.get("pageNo", 1)
        if (cleanScroll and scrollId) or (data.get('isfenye') == 'y'):
            print('clear......')
            try:
                self.es.clear_scroll(scroll_id=scrollId)
                scrollId = None
            except Exception as e:
                logger.error("clear scroll failed %s" % e)
                # return str(e)
        if scrollId and (not isinstance(scrollId, int)):
            print('scoll...')
            try:
                query_data = self.es.scroll(scroll_id=scrollId, scroll='180s')
                query_data['pageNo'] = pageNo + 1
                return self.result_data(query_data)
            except Exception as e:
                logger.error("search scroll failed %s" % e)
                # return str(e)
        body = self.query_body(data)
        body_pro = {
            "size": pageSize,
            "from": (pageNo - 1) * pageSize,
            "timeout": "60s",
            "query": body,
            "sort": {"timestamp": {"order": sort}},
            "highlight": {
                "pre_tags": ['<span class="highlighterKeyWord">'],
                "post_tags": ["</span>"],
                "number_of_fragments": 0,
                "fields": {"message": {}},
            },
        }
        param_dict = {
            'scroll': "180s",
            'typed_keys': '_doc',
            'body': body_pro,
            'index': search_index,
        }
        if data.get('isfenye') == 'y':
            param_dict.pop('scroll')
        else:
            # if data.get('lastItemTime') and data.get('scrollId')=='':
            #     param_dict.pop('scroll')
            # else:
            param_dict['body'].pop('from')
        # logger.info(f'param_dict>>{param_dict}')
        try:
            query_data = self.es.search(**param_dict)
        except Exception as e:
            print(e)
            if pageNo * pageSize >= 10000:
                raise ValueError(f'page_no{pageNo} * page_size{pageSize} over 10000,分页只支持10000以内等')
        query_data['pageNo'] = pageNo + 1
        resp_data = self.result_data(query_data)
        # shortMessage_front = data.get('shortMessage')
        # if shortMessage_front:
        #     shortMessage_front = shortMessage_front.replace('<span class=\"highlighterKeyWord\">', '').replace(
        #         '</span>', '')
        #     locate_flag = 0
        #     for i, item in enumerate(resp_data.get('messages')):
        #         timestamp_resp = item.get('timestamp')
        #         message = item.get('message')
        #         if str(timestamp_resp) == str(timestamp) and shortMessage_front in message:
        #             locate_flag = i
        #     if locate_flag:
        #         resp_data = resp_data[:locate_flag]

        return resp_data

    def es_current(self, data):
        query_data = dict()
        search_index = self.get_search_index(data)
        sort = data.get("sort", None)
        if sort == "descending":
            sort = "desc"
        elif sort == "ascending":
            sort = "asc"

        pageSize = data.get("pageSize", 50)
        body = self.query_body(data)
        query_data = self.es.search(
            body={
                "size": pageSize,
                "timeout": "60s",
                "query": body,
                "sort": {"timestamp": {"order": sort}},
                "highlight": {
                    "pre_tags": ['<span class="highlighterKeyWord">'],
                    "post_tags": ["</span>"],
                    "number_of_fragments": 0,
                    "fields": {"message": {}},
                },
            },
            index=search_index,
            typed_keys="_doc",
        )

        return self.result_data(query_data)

    def es_locate(self, data):

        type_ = data.get("type", None)
        scrollId = data.get("scrollId", None)
        search_index = self.get_search_index(data)
        request = []
        query = self.query_body(data)

        if type_ and type_ == "pre":
            if scrollId:
                try:
                    resp = self.es.scroll(scroll_id=scrollId, scroll="180s")
                    firstHalfMessages = self.message_data(resp)
                    result_data = {}
                    firstHalfMessages.reverse()
                    result_data["scrollId"] = resp.get("_scroll_id", "")
                    result_data["firstHalfMessages"] = firstHalfMessages
                    result_data["secondHalfMessages"] = []
                    result_data["totalHits"] = resp["hits"]["total"]["value"]
                    result_data["tookInSeconds"] = resp.get("took", 0)
                    return result_data
                except Exception as e:
                    logger.error("search scroll failed %s" % e)

            query["bool"]["must"].append(
                {
                    "range": {
                        "timestamp": {
                            # "gt": time_format(data["lastItemTime"])
                            "gt": data["lastItemTime"]
                        }
                    }
                }
            )
            # print(query)
            req_body = {
                "size": data["pageSize"],
                "timeout": "60s",
                "query": query,
                "sort": {"timestamp": {"order": "asc"}},
            }
            print(req_body)
            resp = self.es.search(
                scroll="180s",
                body=req_body,
                index=search_index,
                typed_keys="_doc",
            )
            firstHalfMessages = self.message_data(resp)
            result_data = {}
            firstHalfMessages.reverse()
            result_data["scrollId"] = resp.get("_scroll_id", "")
            result_data["firstHalfMessages"] = firstHalfMessages
            result_data["secondHalfMessages"] = []
            result_data["totalHits"] = resp["hits"]["total"]["value"]
            result_data["tookInSeconds"] = resp.get("took", 0)
            return result_data
        elif type_ and type_ == "next":
            if scrollId:
                # print(scrollId)
                try:
                    resp = self.es.scroll(scroll_id=scrollId, scroll="180s")
                    # print(resp)
                    secondHalfMessages = self.message_data(resp)
                    result_data = {}
                    # firstHalfMessages.reverse()
                    result_data["scrollId"] = resp.get("_scroll_id", "")
                    result_data["firstHalfMessages"] = []
                    result_data["secondHalfMessages"] = secondHalfMessages
                    result_data["totalHits"] = resp["hits"]["total"]["value"]
                    result_data["tookInSeconds"] = resp.get("took", 0)
                    return result_data
                except Exception as e:
                    logger.error("search scroll failed %s" % e)

            query["bool"]["must"].append(
                {
                    "range": {
                        "timestamp": {
                            # "gt": time_format(data["lastItemTime"])
                            "lte": data["lastItemTime"]
                        }
                    }
                }
            )
            req_body = {
                "size": data["pageSize"],
                "timeout": "60s",
                "query": query,
                "sort": {"timestamp": {"order": "desc"}},
            }
            resp = self.es.search(
                scroll="180s",
                body=req_body,
                index=search_index,
                typed_keys="_doc",
            )
            secondHalfMessages = self.message_data(resp)
            result_data = {}
            result_data["scrollId"] = resp.get("_scroll_id", "")
            result_data["firstHalfMessages"] = []
            result_data["secondHalfMessages"] = secondHalfMessages
            result_data["totalHits"] = resp["hits"]["total"]["value"]
            result_data["tookInSeconds"] = resp.get("took", 0)
            return result_data
        else:
            query_gt = deepcopy(query)
            # print(query_gt)
            query_gt["bool"]["must"].append(
                {
                    "range": {
                        "timestamp": {
                            # "gt": time_format(data["lastItemTime"])
                            "gt": data["lastItemTime"]
                        }
                    }
                }
            )
            query_lte = deepcopy(query)
            query_lte["bool"]["must"].append(
                {
                    "range": {
                        "timestamp": {
                            # "lte": time_format(data["lastItemTime"])
                            "lte": data["lastItemTime"]
                        }
                    }
                }
            )
            # print(query_lte)

            req_head = {}
            req_body_gt = {
                "size": data["pageSize"],
                "timeout": "60s",
                "query": query_gt,
                "sort": {"timestamp": {"order": "asc"}},
            }
            request.extend([req_head, req_body_gt])
            req_body_lte = {
                "size": data["pageSize"],
                "timeout": "60s",
                "query": query_lte,
                "sort": {"timestamp": {"order": "desc"}},
            }

            request.extend([req_head, req_body_lte])
            # pprint(request)
            resp = self.es.msearch(body=request, index=search_index)
            # pprint(resp)
            # pprint(resp["responses"][0])
            firstHalfMessages = self.message_data(resp["responses"][0])
            secondHalfMessages = self.message_data(resp["responses"][1])
            result_data = {}
            firstHalfMessages.reverse()
            result_data["firstHalfMessages"] = firstHalfMessages
            result_data["secondHalfMessages"] = secondHalfMessages
            result_data["totalHits"] = (
                    resp["responses"][0]["hits"]["total"]["value"]
                    + resp["responses"][1]["hits"]["total"]["value"]
            )
            result_data["tookInSeconds"] = resp["responses"][0].get("took", 0) + resp[
                "responses"
            ][1].get("took", 0)
            return result_data

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

    def query_body(self, data, type_func='other'):
        # print(data)
        startTime = data.get("startTime", 0)
        endTime = data.get("endTime", 0)
        lastItemTime = data.get("lastItemTime", 0)
        cluster = data.get("cluster", None)
        env = data.get("env", None)

        instance = data.get("instance", 'AllInstances')

        service = data.get("service", None)
        level = data.get("level", None)
        pid = data.get("pid", None)
        thread = data.get("thread", None)
        traceId = data.get("traceId", None)
        request_time = data.get("request_time", None)
        upstream_time = data.get("upstream_time", None)
        message = data.get("message", None)
        queryType = data.get("queryType", None)
        sort = data.get("sort", None)
        # gate_filed
        domain = data.get('domain')
        client_ip = data.get('client_ip')
        request_uri = data.get('request_uri')
        upstream_addr = data.get('upstream_addr')
        status = data.get('status')
        request_methods = data.get('request_methods')
        not_message = data.get("not_message", [])
        filterlocate = data.get('filterlocate', '')
        if sort == "descending":
            sort = "desc"
        elif sort == "ascending":
            sort = "asc"
        filterflag = data.get('filterflag', False)

        query = {}
        query["bool"] = {}
        query["bool"]["must"] = []
        if cluster is not None:
            cluster = {"term": {"cluster": cluster}}
            query["bool"]["must"].append(cluster)

        if env is not None:
            env = {"term": {"env": env}}
            query["bool"]["must"].append(env)
        if service:
            service = {"match": {"service": service}}
            query["bool"]["must"].append(service)
        if instance and not (instance == 'AllInstances'):
            query["bool"]["must"].append({"match_phrase": {"source": instance}})
        if filterflag:
            allignore = data.get('allignore', '')
            query["bool"]["must_not"] = [{"match_phrase": {"message": i}} for i in allignore.split('|#|')]
        if domain:
            match_ = {"match": {"host": domain}}
            query["bool"]["must"].append(match_)
        if pid is not None:
            pid = {"term": {"pid": pid}}
            query["bool"]["must"].append(pid)
        if queryType != "LOCATING" and filterlocate != 'y':
            print('cone to hear>>>>>>>>>>>>>')
            if not_message:
                not_message = [{"match_phrase": {"message": i}} for i in not_message]
                query["bool"]["must_not"] = not_message
            if thread is not None:
                thread = {"term": {"thread": thread}}
                query["bool"]["must"].append(thread)
            if traceId is not None:
                traceId = {"term": {"traceId": traceId}}
                query["bool"]["must"].append(traceId)
            if level is not None:
                level = {"match": {"level": level}}
                query["bool"]["must"].append(level)

            # gate_add
            if client_ip:
                term_ = {"term": {"remote_addr": client_ip}}
                query["bool"]["must"].append(term_)
            if request_uri:
                term_ = {"match": ({"request_uri": {"query": request_uri, "operator": "and"}})}
                # term_ = {"term": {"request_uri": request_uri}}
                query["bool"]["must"].append(term_)
            if upstream_addr:
                term_ = {"term": {"upstream_addr": upstream_addr}}
                query["bool"]["must"].append(term_)
            if status:
                should_dict = {'bool': {'should': []}}
                for item in status.split(','):
                    match_ = {"term": {"status": item}}
                    should_dict['bool']['should'].append(match_)
                query["bool"]["must"].append(should_dict)
            if request_methods:
                match_ = {"match": {"request_method": request_methods}}
                query["bool"]["must"].append(match_)
            if message:
                if queryType == "FUZZY":
                    message = {"match_phrase": {"message": message}}
                    query["bool"]["must"].append(message)
                elif queryType == "NEGATE":
                    query["bool"]["must_not"] = [{"match_phrase": {"message": i}} for i in message.split('|')]
                else:
                    message = {
                        # "match_all": {}
                        "match": ({"message": {"query": message, "operator": "and"}})
                    }
                    query["bool"]["must"].append(message)
            if request_time:
                if '>' in request_time or '=' in request_time or '<' in request_time:
                    request_time_filter = self.create_filter(request_time, 'request_time')
                    if request_time_filter:
                        query["bool"]["must"].append(request_time_filter)
            if upstream_time:
                if '>' in upstream_time or '=' in upstream_time or '<' in upstream_time:
                    upstream_time_filter = self.create_filter(upstream_time, 'upstream_response_time')
                    if upstream_time_filter:
                        query["bool"]["must"].append(upstream_time_filter)
            if startTime > 0 and endTime > 0:
                timestamp = {
                    "range": {
                        "timestamp": {
                            # "gte": time_format(startTime),
                            "gte": startTime,
                            # "lt": time_format(endTime)
                            "lt": endTime,
                        }
                    }
                }
                query["bool"]["must"].append(timestamp)
            elif startTime > 0:
                timestamp = {
                    "range": {
                        "timestamp": {
                            # "gte": time_format(startTime)
                            "gte": startTime
                        }
                    }
                }
                query["bool"]["must"].append(timestamp)
            elif endTime > 0:
                # timestamp = {"range": {"timestamp": {"lt": time_format(endTime)}}}
                timestamp = {"range": {"timestamp": {"lt": endTime}}}
                query["bool"]["must"].append(timestamp)
            if not type_func == 'query':
                if lastItemTime is not None and lastItemTime > 0:
                    if sort == "asc":
                        timestamp = {
                            "range": {
                                "timestamp": {
                                    # "gt": time_format(lastItemTime)
                                    "gt": lastItemTime
                                }
                            }
                        }
                        query["bool"]["must"].append(timestamp)
                    else:
                        timestamp = {
                            "range": {
                                "timestamp": {
                                    # "lt": time_format(lastItemTime)
                                    "lt": lastItemTime
                                }
                            }
                        }
                        query["bool"]["must"].append(timestamp)
        elif queryType == "LOCATING" and filterlocate == 'y':
            if message:
                if queryType == "FUZZY":
                    message = {"match_phrase": {"message": message}}
                    query["bool"]["must"].append(message)
                elif queryType == "NEGATE":
                    query["bool"]["must_not"] = [{"match_phrase": {"message": i}} for i in message.split('|')]
                else:
                    message = {
                        # "match_all": {}
                        "match": ({"message": {"query": message, "operator": "and"}})
                    }
                    query["bool"]["must"].append(message)

            if level is not None:
                level = {"match": {"level": level}}
                query["bool"]["must"].append(level)

        return query

    def chart_body(self, data, ignore_type='allignore'):
        startTime = data.get("fromTime", 0)
        endTime = data.get("toTime", 0)
        level = data.get("level", None)
        message = data.get("message", None)
        queryType = data.get("queryType", 'FUZZY')
        filterflag = data.get('filterflag', False)
        allignore = data.get('allignore', '')
        specignore = data.get('specignore', '')
        query = {}
        query["bool"] = {}
        query["bool"]["must"] = []
        if filterflag:
            if ignore_type == 'allignore':
                ignore_str = allignore
            else:
                ignore_str = specignore
            query["bool"]["must_not"] = [{"match_phrase": {"message": i}} for i in ignore_str.split('|#|')]
        if level is not None:
            level = {"match": {"level": level}}
            query["bool"]["must"].append(level)

        if message:
            if queryType == "FUZZY":
                message = {"fuzzy": {"message": message}}
                query["bool"]["must"].append(message)
            else:
                message = {
                    "match": ({"message": {"query": message, "operator": "and"}})
                }
                query["bool"]["must"].append(message)
        if startTime > 0 and endTime > 0:
            timestamp = {
                "range": {
                    "timestamp": {
                        # "gte": time_format(startTime),
                        "gte": startTime,
                        # "lt": time_format(endTime)
                        "lt": endTime,
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif startTime > 0:
            timestamp = {
                "range": {
                    "timestamp": {
                        # "gte": time_format(startTime)
                        "gte": startTime
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif endTime > 0:
            # timestamp = {"range": {"timestamp": {"lt": time_format(endTime)}}}
            timestamp = {"range": {"timestamp": {"lt": endTime}}}
            query["bool"]["must"].append(timestamp)

        return query

    def agg_body(self, data):
        startTime = strtime2int(data['fromTime'])
        endTime = strtime2int(data['toTime'])
        time_field =  COMPONENT_DICT[data.get("component", '')]['time_field']
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

    def map_fun(self, data):
        map_data = {}
        map_data = data["_source"]
        if "highlight" in data:
            for k, v in data["highlight"].items():
                v_S = str()
                for i in v:
                    v_S = v_S + i
                map_data[k] = v_S
        shortOffset = data.get("shortOffset", 0)
        re_message = re.search(r"\[-\[(.*)\]-\]", map_data["message"])
        if shortOffset > 0:
            if (
                    map_data["message"] is None
                    or shortOffset <= 0
                    or shortOffset > len(map_data["message"]) - 1
            ):
                map_data["shortMessage"] = map_data["message"]
        elif map_data["message"] and re_message:
            map_data["shortMessage"] = re_message.group(0)
        else:
            map_data["shortMessage"] = map_data["message"][shortOffset:]
        return map_data

    def map_fun_origin(self, data):
        map_data = {}
        map_data = data["_source"]
        return map_data

    def message_data(self, data):
        # result_data = {}
        try:
            if len(data["hits"]["hits"]) > 0:
                message = list(map(self.map_fun, data["hits"]["hits"]))
            else:
                message = []
        except:
            message = []

        return message

    def result_data(self, data):
        result_data = {}
        result_data["messages"] = self.message_data(data)
        try:
            result_data["totalHits"] = data["hits"]["total"]["value"]
        except:
            result_data["totalHits"] = 0
        result_data["tookInSeconds"] = data.get("took", 0)
        result_data["scrollId"] = data.get("_scroll_id", "")
        result_data["pageNo"] = data.get("pageNo", 1)

        return result_data

    @staticmethod
    def count_kuadu(fromTime, toTime):
        kuadu = int((toTime - fromTime) / 1000)
        if kuadu > 60 and kuadu <= 60 * 10:
            step = '1m'
        elif kuadu > 60 * 10 and kuadu <= 60 * 60 * 2:
            step = '5m'
        elif kuadu > 60 * 60 * 2 and kuadu <= 60 * 60 * 24:
            step = '1h'
        elif kuadu > 60 * 60 * 24 and kuadu <= 60 * 60 * 24 * 3:
            step = '4h'
        elif kuadu > 60 * 60 * 24 * 3:
            step = '1d'
        else:
            step = '5s'
        return step

    def es_alarmapi(self, request_data):
        component = request_data.get('component', '')
        aggs = request_data.get('aggs', '')
        size = request_data.get('size', '')
        _source = request_data.get('_source', '')

        if component:
            search_index = COMPONENT_DICT[component]['index']
            # search_index = 'aops-apisix-apisix-1zdd8e3f-8941-4606-82df-178593de197c-2023.10.08'
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
        print(param_dict)
        query_data = self.es.search(**param_dict)
        es_datas = list(map(self.map_fun_origin, query_data["hits"]["hits"]))
        res_data = {'data': es_datas, 'aggregations': query_data.get('aggregations')}
        return res_data

    def es_aggrations(self, request_data, aggs):
        domain = request_data.get('domain', '')
        if domain:
            search_index = "ng_log_" + domain + "_*"
        else:
            search_index = "ng_log_*"

        body = self.agg_body(request_data)
        body_pro = {
            "size": 0,
            "timeout": "60s",
            "query": body,
            "aggs": aggs
        }
        param_dict = {
            'body': body_pro,
            'index': search_index,
        }
        query_data = self.es.search(**param_dict)
        res_data = {'data': query_data["aggregations"]}
        return res_data

    def es_aggrations_service(self, request_data, aggs):
        id_ = request_data.get('id', '')
        service, env = id_.split('.')
        startTime = request_data.get("fromTimeint", 0)
        endTime = request_data.get("toTimeint", 0)

        query = {}
        query["bool"] = {}
        query["bool"]["must"] = []
        if env is not None:
            query["bool"]["must"].append({"term": {"env": env}})
        if service:
            query["bool"]["must"].append({"match": {"service": id_}})
        if startTime > 0 and endTime > 0:
            timestamp = {
                "range": {
                    "timestamp": {
                        # "gte": time_format(startTime),
                        "gte": startTime,
                        # "lt": time_format(endTime)
                        "lt": endTime,
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif startTime > 0:
            timestamp = {
                "range": {
                    "timestamp": {
                        # "gte": time_format(startTime)
                        "gte": startTime
                    }
                }
            }
            query["bool"]["must"].append(timestamp)
        elif endTime > 0:
            # timestamp = {"range": {"timestamp": {"lt": time_format(endTime)}}}
            timestamp = {"range": {"timestamp": {"lt": endTime}}}
            query["bool"]["must"].append(timestamp)

        body_pro = {
            "size": 0,
            "timeout": "60s",
            "query": query,
            "aggs": aggs
        }
        if service:
            index = "%s_%s_" % (env, service)
        elif env:
            index = env + "_"
        else:
            index = ""
        search_index = "ap_log_" + index + "*"
        param_dict = {
            'body': body_pro,
            'index': search_index,
        }
        query_data = self.es.search(**param_dict)
        res_data = {'data': query_data["aggregations"]}
        return res_data

def strtime2int(time_str,format='%Y-%m-%dT%H:%M:%S'):
    time_int = int(time.mktime(time.strptime(time_str.split('.')[0], format)) * 1000)
    return time_int
if __name__ == "__main__":

    # data = {
    #     "component": "yewu-apisix",
    #     "fromTime": '2023-10-16T12:33:24.366',
    #     "toTime": '2023-10-16T13:33:24.366',
    #     "size":0,
    #     "aggs":{
    #         "resp":
    #             {"terms":
    #                  { "field": "http_host.keyword",
    #                     "size":9999
    #                    }
    #              }
    #     }
    # }

    #90 50 区域响应时间分布
    # data = {
    #     "component": "yewu-apisix",
    #     "fromTime": '2023-10-16T12:33:24.366',
    #     "toTime": '2023-10-16T13:33:24.366',
    #     "size": 0,
    #     "aggs": {
    #         "time_slice": {
    #             "date_histogram": {
    #                 "field": "@timestamp",
    #                 "fixed_interval": '5m'
    #             },
    #             "aggs": {
    #                 "maxResp": {"max": {"field": "request_time"}},
    #                 "request_time_outlier": {
    #                     "percentiles": {
    #                         "field": "request_time",
    #                         "percents": [50, 90]
    #                     }
    #                 }
    #             }
    #         }
    #     }
    # }


    #restime
    # data = {
    #     "component": "yewu-apisix",
    #     "fromTime": '2023-10-16T12:33:24.366',
    #     "toTime": '2023-10-16T13:33:24.366',
    #     "size": 0,
    #     "aggs":{
    #     "pieresp":
    #         {"terms":
    #              { "script":
    #                 {"source": "def request_time=doc['request_time'].value;def reqeust_str = '<1s';if(request_time<1){reqeust_str='<1s'}else if(request_time<2){reqeust_str='1-2s'}else if(request_time<5){reqeust_str='2-5s'}else if(request_time<2){reqeust_str='1-2s'}else if(request_time<10){reqeust_str='5-10s'}else if(request_time<10){reqeust_str='10-15s'}else{reqeust_str='>15s'}return reqeust_str"},
    #                 "size":9999
    #                }
    #          }
    # }
    # }
    #区域流入流出量（Mb）
    # data = {
    #     "component": "yewu-apisix",
    #     "fromTime": '2023-10-16T12:33:24.366',
    #     "toTime": '2023-10-16T13:33:24.366',
    #     "size": 0,
    #     "aggs":  {
    #     "time_slice":{
    #        "date_histogram": {
    #             "field": "@timestamp",
    #             "fixed_interval": '5m'
    #           },
    #         "aggs":{
    #           "netout":{"sum":{"field":"bytes_sent"}},
    #           "netin":{"sum":{"field":"request_length"}}
    #         }
    #      }
    #   }
    # }

    data = {
        "component": "yewu-apisix",
        "fromTime": '2023-10-16T12:33:24.366',
        "toTime": '2023-10-16T13:33:24.366',
        "size": 0,
        "aggs": {
        "pieresp":
            {"terms":
                 { "script":
                     {
                         "lang": "painless",
                         "source": "doc['status.keyword'].value.substring(0, 1) + 'xx' + '_' + doc['request_method.keyword'].value"
                     },

                     "size":9999
                   }
             }
    }
    }

    # host table
    data = {
        "component": "yewu-apisix",
        "fromTime": '2023-10-16T12:33:24.366',
        "toTime": '2023-10-16T13:33:24.366',
        "size": 0,
        "query":{
            "bool":{
                "must":[
                    {"term": {"http_host": "support.changyan.com"}}
                ]
            }
        },
        "aggs": {
            "resp":
                {
                    "terms":
                     {"field": "uri.keyword",
                        "size":9999
                     },
                    "aggs":{
                        "errorCount":{
                            "filter":{
                                "bool":{"must":[
                                    {"term": {"status": "304"}},
                                    {"term": {"status": "499"}},
                                ]}
                            }



                        },
                        "maxResp": {"max": {"field": "request_time"}},
                        "net_out":{"sum":{"field":"bytes_sent"}},
                        "net_in":{"sum":{"field":"request_length"}},
                        "request_time_outlier": {
                        "percentiles": {
                          "field": "request_time",
                          "percents": [ 50, 90]
                        }
                          },
                        "uv": {
                            "cardinality": {
                                "field": "remote_addr.keyword"
                            }
                        }
                    }
                 }
        }
    }

    es = EsOperation('10.110.1.11:9113','aops','1qaZwsx3edcrfv')
    print(es.es_alarmapi(data))
