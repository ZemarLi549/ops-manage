from utils.logger import logger
from elasticsearch import Elasticsearch
from ops_alarm.settings import ES_HOSTS,ES_USERNAME,ES_PWD
from datetime import datetime
import traceback
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
        self.es = Elasticsearch(es_host_list, http_auth=(self.es_username, self.es_password), timeout=3600,verify_certs=False)
    def insert_data(self,data):
        # 获取当前日期，作为索引名称的一部分
        today_date = datetime.now().strftime("%Y.%m.%d")
        index_name = f"opsalarm-{today_date}"  # 例如：logs-2023.11.15

        # 创建索引的 mapping（假设存储的数据是日志）
        mapping = {
            "mappings": {
                "properties": {
                    "startsAt": {"type": "date"},
                    "alarm_id": {"type": "integer"},
                    "srmid": {"type": "integer"},
                    "labels": {"type": "text"},
                    "alarm_summary": {"type": "text"},
                    "alarm_desc": {"type": "text"},
                    "execution": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "severity": {"type": "keyword"},
                    "alarm_send": {
                        "type": "object"
                    },
                    "identity_tag_kv": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"# 用于聚合操作的关键字类型子字段
                            },
                        }
                    },
                    "alertname": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"# 用于聚合操作的关键字类型子字段
                            },
                        }
                    },
                    "job": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"# 用于聚合操作的关键字类型子字段
                            },
                        }
                    },
                    "instance": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"# 用于聚合操作的关键字类型子字段
                            },
                        }
                    },
                    "source": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"# 用于聚合操作的关键字类型子字段
                            },
                        }
                    },
                    "group": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"# 用于聚合操作的关键字类型子字段
                            },
                        }
                    },

                }
            }
        }

        # 创建索引
        if not self.es.indices.exists(index=index_name):
            try:
                self.es.indices.create(index=index_name, body=mapping)
            except Exception as e:
                logger.warning(f'maybe不必再创建索引了,{e}')

        self.es.index(index=index_name, body=data)

def init_and_save(data):
    logger.info(f'begin save:{data.get("alarm_id","")}')
    try:
        # 连接 Elasticsearch
        es = EsOperation()
        es.insert_data(data)
    except Exception as e:
        logger.error(f'save es err>>>{e}')
        print(traceback.format_exc())
def save_alarm(alarm_to,post_data):
    customSend = post_data.get('customSend',{})
    if customSend:
        alarm_to = customSend
    alarm_status = post_data.get('status','firing')
    startsAt = post_data.get('startsAt','')
    alarm_id= post_data.get('alarm_id',0)
    labels = post_data.get('labels',{})
    identity_tag_kv = post_data.get('identity_tag_kv',{})
    execution = post_data.get('execution','一般告警')
    alarm_summary = post_data.get('annotations',{}).get('summary','')
    logger.info(f'save_alarm>>>{alarm_summary}')
    alarm_desc = post_data.get('annotations',{}).get('description','')
    alarm_send = {}
    for alarm_type,alarm_list in alarm_to.items():
        send_to_all = set()
        for alarm_detail in alarm_list:
            send_to = alarm_detail.get('send_to',[])
            for username in send_to:
                send_to_all.add(username)
        alarm_send[alarm_type] = ','.join(list(send_to_all))
    # 存储数据到索引中
    data = {
        "startsAt": datetime.strptime(startsAt, '%Y-%m-%d %H:%M:%S'),
        "alarm_id": int(alarm_id),
        "srmid": int(labels.get('id',1)),
        "labels":','.join([f'{key}={val}' for key,val in labels.items()]),
        "alarm_summary":alarm_summary,
        "alarm_desc":alarm_desc,
        "execution":execution,
        "status":alarm_status,
        "severity":labels.get('severity','一般'),
        "alarm_send":alarm_send,
        "identity_tag_kv":','.join([f'{key}={val}' for key,val in identity_tag_kv.items()]),
        "alertname":labels.get('alertname',''),
        "job":labels.get('job',''),
        "instance":labels.get('instance',''),
        "source":labels.get('source',''),
        "group":labels.get('group',''),
    }
    init_and_save(data)
    pass