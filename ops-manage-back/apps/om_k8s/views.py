# -*- coding: utf-8 -*-
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
import requests
from django.shortcuts import HttpResponse
from apps.common.renderers import MyJSONRenderer
from apps.common.try_catch import try_catch
from rest_framework import status as http_status
import logging
from apps.om_k8s.models import *
from .serializers import *
from apps.common.tools import encrypt,decrypt
from apps.common.ops_k8s import OpsK8s
import base64
from apps.common.dbopr import get_func,put_func,delete_func,to_underline
logger = logging.getLogger(__name__)
# Create your views here.

class ClusterInfoView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        clusterId = int(query_params['clusterId'])

        params = []
        condition_sql = ' where id IS NOT NULL '
        if clusterId:
            condition_sql += ' and (id=%s) '
            params.append("{}".format(clusterId))
        res_dict = get_func('id', query_params, condition_sql, params, 'k8s_cluster',selfields="*")
        res_dict['data'] = res_dict['data'][0]
        return Response(res_dict, http_status.HTTP_200_OK)


class ClusterView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        params = []
        condition_sql = ' where id IS NOT NULL '
        res_dict = get_func('id', query_params, condition_sql, params, 'k8s_cluster',selfields="*")
        data = res_dict['data']
        for jiqun in data:
            k8s_config = jiqun['config']
            k8sService = OpsK8s(k8s_config)
            try:
                items = k8sService.list_nodes().items
                version = ''
                if items:
                    version = items[0].status.node_info.kubelet_version
                jiqun['version'] = version
                jiqun['nodeNumber'] = len(items)
            except Exception as e:
                jiqun['version'] = e
                jiqun['nodeNumber'] = 0
        res_dict['data'] = data

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        logger.info("request.data:%s", request.data)
        request_data = request.data
        request_data = to_underline(request_data)

        login_user = request.username if hasattr(request, 'username') else 'sys'
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, Cluster, Clusterer)
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        logger.info("params:%s", query_params)
        clusterIds = query_params.get('clusterIds', [])
        if not clusterIds:
            clusterIds = [query_params['id']]

        resp = delete_func('id', clusterIds, Cluster)
        return Response(resp, http_status.HTTP_200_OK)
    
    

class NodeListView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        page = int(query_params.get('page',1))
        size = int(query_params.get('size',10))
        clusterId = int(query_params['clusterId'])
        name = query_params.get('filterBy')

        clusterObj = Cluster.objects.filter(id=clusterId).first()
        config = clusterObj.config
        k8sService = OpsK8s(config)

        kwargs = {
            'watch': False,
            'timeout_seconds': 180,
        }
        # if name:
        #     kwargs['field_selector'] = f'metadata.name={name.strip().replace(",","")}'
        node_items = k8sService.list_nodes(**kwargs).items
        if name:
            node_items = [node for node in node_items if name in node.metadata.name]
        node_items_page = node_items[(page-1)*size:page*size]
        listMeta = {'totalItems':len(node_items)}
        nodes = []
        for i in node_items_page:
            labels = i.metadata.labels
            roles = []
            for key, val in labels.items():
                if 'node-role.kubernetes.io' in key:
                    role = key.split('/')[-1]
                    roles.append(role)
                elif 'role' in key:
                    if '/' in key:
                        role = key.split('/')[-1]
                        roles.append(role)
                    else:
                        if val: roles.append(val)

            node_ip = i.status.addresses[0].address
            ready = i.status.conditions[-1].status
            kubelet_version = i.status.node_info.kubelet_version
            os_image = i.status.node_info.os_image
            createdAt = i.metadata.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%S')
            container_runtime_version = i.status.node_info.container_runtime_version
            unschedulable = i.spec.unschedulable
            node_name = i.metadata.name
            # try:
            #     dict_resource = k8sService.list_node_pods(node_name)
            # except:
            #     dict_resource = {}
            # pod_count = dict_resource.get('count',0)
            # limits_cpu = dict_resource.get('limits_cpu',0)
            #
            # requests_cpu = dict_resource.get('requests_cpu',0)
            # requests_mem = dict_resource.get('requests_mem',0)
            # limits_mem = dict_resource.get('limits_mem',0)
            print('cpu>>>',i.status.capacity.get('cpu'))
            print('mem>>>',i.status.allocatable.get('memory'))
            cpuCapacity = int(i.status.capacity.get('cpu'))
            # cpuCapacity = int(i.status.capacity.get('cpu')) * 1000
            memoryCapacity = i.status.allocatable.get('memory')
            # memoryCapacity = int(i.status.allocatable.get('memory').replace('Ki', '')) * 1024
            podCapacity = int(i.status.capacity.get('pods', 0))

            dict_ = {
                "ready": ready,
                "nodeIP": node_ip,
                "roles": roles,
                'unschedulable': unschedulable,
                'allocatedResources': {
                    'allocatedPods': 0,
                    'cpuCapacity': cpuCapacity,
                    'cpuLimits': 0,
                    # 'cpuLimitsFraction': round(0 / cpuCapacity * 100,3),
                    'cpuRequests': 0,
                    # 'cpuRequestsFraction': round(0 / cpuCapacity * 100,3),
                    'memoryCapacity': memoryCapacity,
                    'memoryRequests': 0,
                    'memoryLimits': 0,
                    # 'memoryLimitsFraction': round(0 / memoryCapacity * 100,3),
                    # 'memoryRequestsFraction': round(0 / memoryCapacity * 100,3),
                    'podCapacity': podCapacity,
                    # 'podFraction': round(0 / podCapacity * 100,3),
                },
                'objectMeta': {
                    "name": node_name,
                    "labels": labels,
                    'createdAt':createdAt
                },
                'nodeInfo': {
                    'containerRuntimeVersion': container_runtime_version,
                    'osImage': os_image,
                    'kubeletVersion': kubelet_version,
                    # 'architecture': i.status.node_info.architecture,
                    # 'bootID': i.status.node_info.boot_id,
                    # 'kernelVersion': i.status.node_info.kernel_version,
                    # 'kubeProxyVersion': i.status.node_info.kube_proxy_version,
                    # 'machineID': i.status.node_info.machine_id,
                    # 'operatingSystem': i.status.node_info.operating_system,
                    # 'systemUUID': i.status.node_info.system_uuid,
                },
            }
            nodes.append(dict_)
        print(len(nodes),'>>>>>>>')
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': {'listMeta':listMeta,'nodes':nodes}, 'count': len(node_items)}

        return Response(res_dict, http_status.HTTP_200_OK)


class NodeDetailView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        
        clusterId = int(query_params['clusterId'])
        name = query_params['name']
        clusterObj = Cluster.objects.filter(id=clusterId).first()
        config = clusterObj.config
        k8sService = OpsK8s(config)
        node = k8sService.read_node(name=name, dictize=True)

        node_ip = node['status']['addresses'][0]['address']
        ready = node['status']['conditions'][-1]['status']
        node_name = node['metadata']['name']
        try:
            dict_resource = k8sService.list_node_pods(node_name, get_pod=True)
        except Exception as e:
            print(e)
            dict_resource = {}
        pod_count = dict_resource.get('count', 0)
        limits_cpu = dict_resource.get('limits_cpu', 0)
        requests_cpu = dict_resource.get('requests_cpu', 0)
        requests_mem = dict_resource.get('requests_mem', 0)
        limits_mem = dict_resource.get('limits_mem', 0)
        cpuCapacity = int(node['status']['capacity'].get('cpu')) * 1000
        memoryCapacity = int(node['status']['allocatable'].get('memory').replace('Ki', '')) * 1024
        podCapacity = int(node['status']['capacity'].get('pods', 0))
        imageList = [item['names'] for item in node['status']['images']]
        dict_ = {
            "addresses": node['status']['addresses'],
            'allocatedResources': {
                'allocatedPods': pod_count,
                'cpuCapacity': cpuCapacity,
                'cpuLimits': limits_cpu,
                'cpuLimitsFraction': round(limits_cpu / cpuCapacity * 100,3),
                'cpuRequests': requests_cpu,
                'cpuRequestsFraction': round(requests_cpu / cpuCapacity * 100,3),
                'memoryCapacity': memoryCapacity,
                'memoryRequests': requests_mem,
                'memoryLimits': limits_mem,
                'memoryLimitsFraction': round(limits_mem / memoryCapacity * 100,3),
                'memoryRequestsFraction': round(requests_mem / memoryCapacity * 100,3),
                'podCapacity': podCapacity,
                'podFraction': round(pod_count / podCapacity * 100,3),
            },
            "conditions": node['status']['conditions'],
            "containerImages": imageList,
            "eventList": {
                "metadata": {
                    "resourceVersion": node['metadata']['resourceVersion']
                },
                "items": []
            },
            "nodeIP": node_ip,
            'nodeInfo': node['status']['nodeInfo'],
            'objectMeta': {
                "annotations": node['metadata']['annotations'],
                "labels": node['metadata']['labels'],
                'name': node['metadata']['name'],
                'creationTimestamp': node['metadata']['creationTimestamp'],
            },
            "phase": "",
            "podCIDR": node['spec'].get('podCIDR',''),
            "podList": {
                "items": dict_resource['podList'],
                "metadata": {
                    "resourceVersion": node['metadata']['resourceVersion']
                },
            },
            "providerID": "",
            "ready": ready,
            "typeMeta": {"kind": "node"},
            "uid": node['metadata']['uid'],
            'unschedulable': node['spec'].get('unschedulable',''),
            "taints": node['spec'].get('taints', [])
        }
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK',
                    'data': dict_, 'count': 1}

        return Response(res_dict, http_status.HTTP_200_OK)


class PodLogView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        clusterId = int(query_params['clusterId'])
        pod = query_params.get('pod','')
        namespace = query_params.get('namespace','')

        clusterObj = Cluster.objects.filter(id=clusterId).first()
        config = clusterObj.config
        k8sService = OpsK8s(config)

        resp = k8sService.get_namespaced_pod_log(name=pod, namespace=namespace)

        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK',
                    'data': {'logs':resp.split('\n')}, 'count': 1}

        return Response(res_dict, http_status.HTTP_200_OK)

class K8sNamespacesView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)

        clusterId = int(query_params['clusterId'])

        clusterObj = Cluster.objects.filter(id=clusterId).first()
        config = clusterObj.config
        k8sService = OpsK8s(config)
        data = k8sService.list_all_namespace()
        data = [item.metadata.name for item in data]
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK',
                    'data': data, 'count': len(data)}

        return Response(res_dict, http_status.HTTP_200_OK)
class K8sEventsView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)

        clusterId = int(query_params['clusterId'])
        namespace = query_params.get('namespace','')

        clusterObj = Cluster.objects.filter(id=clusterId).first()
        config = clusterObj.config
        k8sService = OpsK8s(config)


        kwargs = {
            'limit': 300,
        }
        if namespace:
            kwargs['field_selector'] = f'metadata.namespace={namespace.strip()}'

        events = k8sService.list_cluster_events(**kwargs)
        data = []
        for item in events:
            source = item.get('source', {})
            data.append({
                'type': item.get('type', ''),
                'reason': item.get('reason', ''),
                'kind': source.get('component', '') + ' ' + source.get('host', ''),
                'message': item.get('reason', ''),
                'lastTimestamp': item.get('lastTimestamp', ''),
            })
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK',
                    'data': data, 'count': len(data)}

        return Response(res_dict, http_status.HTTP_200_OK)


class K8sDeploymentsView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)

        clusterId = int(query_params['clusterId'])
        namespace = query_params.get('namespace','')

        clusterObj = Cluster.objects.filter(id=clusterId).first()
        config = clusterObj.config
        k8sService = OpsK8s(config)

        deployments = k8sService.list_deployments(namespace=namespace)

        deployments_list = []
        count = 0
        for item in deployments:
            count+=1
            dict_ = {
                'containerImages': [con['image'] for con in item['spec']['template']['spec']['containers']],
                'deploymentStatus': {
                    'availableReplicas': item['status'].get('availableReplicas', 0),
                    'readyReplicas': item['status'].get('readyReplicas', 0),
                    'replicas': item['status'].get('replicas',0),
                    'unavailableReplicas': item['status'].get('unavailableReplicas', 0),
                    'updatedReplicas': item['status'].get('updatedReplicas', 0),
                },
                'objectMeta': {
                    'annotations': item['metadata']['annotations'],
                    'creationTimestamp': item['metadata']['creationTimestamp'],
                    'labels': item['metadata'].get('labels',[]),
                    'name': item['metadata']['name'],
                    'namespace': item['metadata']['namespace'],
                },
                'typeMeta': {
                    'kind': 'Deployment'
                }
            }
            deployments_list.append(dict_)
        deployments_list.sort(key=lambda x: x['objectMeta'].get('creationTimestamp'),reverse=True)
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK',
                    'data': {
                        'listMeta':{'totalItems':count},
                        'deployments':deployments_list
                    }, 'count': count}

        return Response(res_dict, http_status.HTTP_200_OK)


class K8sServicesView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)

        clusterId = int(query_params['clusterId'])
        namespace = query_params.get('namespace','')

        clusterObj = Cluster.objects.filter(id=clusterId).first()
        config = clusterObj.config
        k8sService = OpsK8s(config)

        deployments = k8sService.list_deployments(namespace=namespace)

        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK',
                    'data': {
                        'listMeta':{'totalItems':count},
                        'deployments':deployments_list
                    }, 'count': count}

        return Response(res_dict, http_status.HTTP_200_OK)