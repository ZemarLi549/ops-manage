# -*- coding:utf-8 -*-
import json, time,os,sys
import django
import logging
logger = logging.getLogger(__name__)
import uuid
from channels.generic.websocket import WebsocketConsumer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ls_base = BASE_DIR.split('/')
PROJECT_DIR = ''
for item in ls_base:
    if item=='ops_release':
        PROJECT_DIR += item
        break
    else:
        PROJECT_DIR += item + '/'
sys.path.append(PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ops_release.settings")
django.setup()
from apps.common.ops_k8s import OpsK8s,K8SStreamThread
from apps.om_k8s.models import Cluster
from asgiref.sync import async_to_sync


class CurrentLog(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(CurrentLog, self).__init__(*args, **kwargs)

    def connect(self):
        self.container_id = self.scope['url_route']['kwargs']['cid']
        self.namespace = self.scope['url_route']['kwargs']['namespace']
        self.cluster_id = self.scope['url_route']['kwargs']['cluster']
        clusterObj = Cluster.objects.filter(id=self.cluster_id).first()
        config = clusterObj.config
        self.k8sService = OpsK8s(config)
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.container_stream = self.k8sService.terminal_start(podname=self.container_id, namespace=self.namespace)
        kub_stream = K8SStreamThread(self, self.container_stream)
        kub_stream.start()
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        try:
            query_params = json.loads(text_data)
            opreation = query_params.get('type', 'input')
            exec_str = query_params.get('input', '')
        except:
            exec_str = text_data
            opreation = 'input'



        if opreation=='input':

            if exec_str:
                self.container_stream.write_stdin(exec_str)

        elif opreation=='resize':
            print(query_params)
            cols = query_params.get('cols',24)
            rows = query_params.get('rows',80)
            self.container_stream.write_channel(4, json.dumps({"Height": int(rows), "Width": int(cols)}))



    def record_resullt(self, user, ans_model, ans_server, ans_argsy):
        print('record finish')

    def disconnect(self, close_code):
        self.container_stream.write_stdin('exit\r')
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
        self.close()


def get_pod_info(podId,nodeName,namespace):
    pod = {
        "metadata": {
            "name": podId,
            "namespace": namespace
        },
        'spec': {
            'restartPolicy': "Never",
            'terminationGracePeriodSeconds': 0,
            'hostPID': True,
            'hostIPC': True,
            'hostNetwork': True,
            'tolerations': [{
                'operator': "Exists"
            }],
            'containers': [{
                'name': "shell",
                'image': "docker.io/alpine:3.9",
                'securityContext': {
                    'privileged': True,
                },
                'command': ["nsenter"],
                'args': ["-t", "1", "-m", "-u", "-i", "-n", "sleep", "14000"]
            }],
            'nodeSelector': {
                "kubernetes.io/hostname": nodeName
            }
        }
    }
    return pod
class NodeShell(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(NodeShell, self).__init__(*args, **kwargs)
    def create_nodeshell(self,pod_body):
        k8sService = OpsK8s(self.config)
        api_response = k8sService.create_namespaced_pod(namespace=self.namespace, body=pod_body)
        max_wait = 60
        i = 0
        while True:
            time.sleep(1)
            i += 1
            if i >= max_wait:
                break
            origin_pod_body_ls = k8sService.list_namespace_pods(namespace=self.namespace, regx=r'' + self.container_id + '.*')
            pod_body_ls = []
            for item in origin_pod_body_ls:
                if item.status.phase.lower() == 'running':
                    pod_body_ls.append(1)
            if pod_body_ls:
                break
            logger.critical(f'namespace:{self.namespace},podname:{self.container_id} pod 未就绪 已等待{i}次，60秒自动判定失败')
    def connect(self):
        self.name = self.scope['url_route']['kwargs']['name']
        self.cluster_id = self.scope['url_route']['kwargs']['cluster']
        self.namespace = 'default'
        uid_str = str(uuid.uuid4()).replace('-', '')
        self.container_id = 'nodeshell-' + uid_str[:10] + '-' + uid_str[11:16]
        pod_body = get_pod_info(self.container_id, self.name,self.namespace)

        clusterObj = Cluster.objects.filter(id=self.cluster_id).first()
        self.config = clusterObj.config
        self.k8sService = OpsK8s(self.config)

        self.create_nodeshell(pod_body)

        self.group_name = self.scope['url_route']['kwargs']['group_name']
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.container_stream = self.k8sService.terminal_start(podname=self.container_id, namespace=self.namespace)
        kub_stream = K8SStreamThread(self, self.container_stream)
        kub_stream.start()
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        try:
            query_params = json.loads(text_data)
            opreation = query_params.get('type', 'input')
            exec_str = query_params.get('input', '')
        except:
            exec_str = text_data
            opreation = 'input'



        if opreation=='input':

            if exec_str:
                self.container_stream.write_stdin(exec_str)

        elif opreation=='resize':
            cols = query_params.get('cols',24)
            rows = query_params.get('rows',80)

            self.container_stream.write_channel(4, json.dumps({"Height": int(rows), "Width": int(cols)}))



    def record_resullt(self, user, ans_model, ans_server, ans_argsy):
        print('record finish')

    def disconnect(self, close_code):
        self.k8sService.delete_namespaced_pod(namespace=self.namespace,name=self.container_id)
        self.container_stream.write_stdin('exit\r')
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
        self.close()
