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
from apps.common.redisclient import getDatasourceInfo,getComponentInfo,RedisClient,get_gate_filter,get_app_filter
from apps.common.dbopr import get_func, put_func, delete_func, to_underline, get_relative_func
import logging

logger = logging.getLogger(__name__)


# from drf_yasg import openapi

# Create your views here.
class DataSourceView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        isSelect = query_params.get('isSelect', False)
        if isSelect:
            obj_list = dict_query('select id,name from l_datasource',
                                  [], camel=False)
            res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': obj_list,
                        'count': len(obj_list)}

            return Response(res_dict, http_status.HTTP_200_OK)
        searchVal = query_params.get('searchVal', None)
        source = query_params.get('source', None)
        condition_sql = ' where 1=1 '
        params = []
        if source:
            condition_sql += ' and (`source`=%s) '
            params.extend([source])
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(`name`,%s) or instr(host,%s)  or instr(logstore,%s) or instr(project_name,%s)) '
            params.extend([searchVal] * 4)

        res_dict = get_func('id', query_params, condition_sql, params, 'l_datasource', selfields="*", camel=False)

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        # request_data = to_underline(request_data)
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, DataSource, DataSourceer)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getsource*')
            if del_keys:
                r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]
        for delete_id in deleteIds:
            try:
                GateConfig.objects.filter(datasource_id=delete_id).delete()
            except Exception as e:
                logger.error(f'GateConfig del error:{e}')
            try:
                AppConfig.objects.filter(datasource_id=delete_id).delete()
            except Exception as e:
                logger.error(f'AppConfig del error:{e}')

        resp = delete_func('id', deleteIds, DataSource)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getsource*')
            if del_keys:
                r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)
class AppListView(APIView):
    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        component = query_params.get('component', None)
        datasource_id = query_params.get('datasource_id', None)
        if component and '|' in component:
            compo_ls = component.split('|')
            component = compo_ls[1]
            datasource_id = int(compo_ls[0])
        condition_sql = ' where 1=1 and isblack="n" '
        params = []
        if component:
            condition_sql += ' and (component=%s) '
            params.extend([component])
        if datasource_id:
            condition_sql += ' and (datasource_id=%s) '
            params.extend([datasource_id])

        res_dict = get_func('id', query_params, condition_sql, params, 'l_appconfig', selfields="app,datasource_id,component", camel=False)
        return Response(res_dict, http_status.HTTP_200_OK)
class GateListView(APIView):
    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        component = query_params.get('component', None)
        datasource_id = query_params.get('datasource_id', None)

        if component and '|' in component:
            compo_ls =  component.split('|')
            component =compo_ls[1]
            datasource_id = int(compo_ls[0])

        condition_sql = ' where 1=1 and isblack="n" '
        params = []
        if component:
            condition_sql += ' and (component=%s) '
            params.extend([component])
        if datasource_id:
            condition_sql += ' and (datasource_id=%s) '
            params.extend([datasource_id])
        res_dict = get_func('id', query_params, condition_sql, params, 'l_gateconfig', selfields="domain,datasource_id,component", camel=False)
        return Response(res_dict, http_status.HTTP_200_OK)
class GateConfigView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        condition_sql = ' where 1=1 '
        params = []
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(a.domain,%s)  or instr(a.component,%s) or instr(b.name,%s) or instr(b.source,%s)) '
            params.extend([searchVal] * 4)

        res_dict = get_relative_func('a.id', 'a.datasource_id=b.id', '"name",b.name,"source",b.source', query_params,
                                     condition_sql, params, 'l_gateconfig', 'l_datasource',
                                     'a.id,a.domain,a.component,a.isblack', camel=False, bagg='source')
        for item in res_dict['data']:
            try:
                source = json.loads(item.pop('source'))[0]
                item['source_name'] = source.get('name', '')
                item['source_type'] = source.get('source', '')
            except Exception as e:
                logger.error(f'加工失败:{e}')
        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, GateConfig, GateConfiger)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getsource_domain*')
            if del_keys:
                r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]
        resp = delete_func('id', deleteIds, GateConfig)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getsource_domain*')
            if del_keys:
                r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)


class AppConfigView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        condition_sql = ' where 1=1 '
        params = []
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(a.app,%s)  or instr(a.component,%s) or instr(b.name,%s) or instr(b.source,%s)) '
            params.extend([searchVal] * 4)

        res_dict = get_relative_func('a.id', 'a.datasource_id=b.id', '"name",b.name,"source",b.source', query_params,
                                     condition_sql, params, 'l_appconfig', 'l_datasource',
                                     'a.id,a.app,a.component,a.isblack', camel=False, bagg='source')
        for item in res_dict['data']:
            try:
                source = json.loads(item.pop('source'))[0]
                item['source_name'] = source.get('name', '')
                item['source_type'] = source.get('source', '')
            except Exception as e:
                logger.error(f'加工失败:{e}')

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, AppConfig, AppConfiger)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getsource_app*')
            if del_keys:
                r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]
        resp = delete_func('id', deleteIds, AppConfig)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getsource_app*')
            if del_keys:
                r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)


class ComponentIndexView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        source = query_params.get('source', None)
        datasource_id = query_params.get('datasource_id', None)
        field_type = query_params.get('field_type', None)
        component = query_params.get('component', None)
        condition_sql = ' where 1=1 '
        params = []
        if datasource_id:
            condition_sql += ' and (`datasource_id`=%s) '
            params.extend([datasource_id])
        if source:
            condition_sql += ' and (`source`=%s) '
            params.extend([source])
        if field_type:
            condition_sql += ' and (`field_type`=%s) '
            params.extend([field_type])
        if component:
            condition_sql += ' and (`component`=%s) '
            params.extend([component])
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(`component`,%s) or instr(index_str,%s)  or instr(field_type,%s) or instr(source,%s)) '
            params.extend([searchVal] * 4)

        res_dict = get_func('id', query_params, condition_sql, params, 'l_component', selfields="*", camel=False)

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        resp = put_func('id', request_data, ComponentIndex, ComponentIndexer)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys(f'getcomp:{request_data.get("component")}*')
            del_keys_2 = r.keys(f'getsource_comp:{request_data.get("component")}*')
            del_keys.extend(del_keys_2)
            if del_keys:
                r.delete(*del_keys)

        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]

        resp = delete_func('id', deleteIds, ComponentIndex)

        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getcomp*')
            del_keys_2 = r.keys(f'getsource_comp:{request_data.get("component")}*')
            del_keys.extend(del_keys_2)
            if del_keys:
                r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del cache err:{e}')
        return Response(resp, http_status.HTTP_200_OK)


class DataCommonSearchView(APIView):
    """
    1. post_data = {
    "datasource_id":1 || esinfo:{'host':''m''username':'',"password":""}
    "is_origin":True,
    "param_dict":{}
    例如： param_dict：{
                'body': {},#原始essql 不加time
                'index': "aops-xxx-*",
            }
    }
    2.post_data = {
                "datasource_id":1,|| app+component ||domain+component
                "index_str":"aops-nginx-nginx-*", || component #传递component 会覆盖
                "time_field":"@timestamp",|| component
                "app":"aops-probe",#可传，针对es 传递了会改变索引(repalce('*',app+'*'))，缩小索引范围，优化
                "fromTime": "2023-10-17T12:54:13",
                "toTime": "2023-10-17T14:54:13",
                "_source":{"includes": ["@timestamp", "http_host"]},
                "size": 0,
                "query":{},
                "aggs": {
                    "resp":
                        {"terms":
                             {
                              "field": "http_host.keyword",
                              "size": 9999
                              }
                         }
                }
            }
    """

    @try_catch
    def post(self, request):
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK,
                    'data': [], 'count': 0}
        request_data = request.data
        logger.info("request_data:%s", request_data)
        post_data = request_data.get('post_data', {})
        esinfo = post_data.get('esinfo')
        datasource_id = post_data.get('datasource_id')
        component = post_data.get('component')
        if component and '|' in component:
            compo_ls = component.split('|')
            component = compo_ls[1]
            datasource_id = int(compo_ls[0])
        domain = post_data.get('domain')
        app = post_data.get('app')

        if not (esinfo or datasource_id or component):
            res_dict['status'] = 'fail'
            res_dict['message'] = ' no (esinfo or datasource_id  or component)'
            return Response(res_dict, http_status.HTTP_200_OK)


        if esinfo:
            es_host = esinfo.get('host', '')
            es_username = esinfo.get('username', '')
            es_pwd = esinfo.get('password', '')
            es = EsOperation(es_host, es_username, es_pwd)
            es_resp = es.es_alarmapi(post_data)
            res_dict['data'] = es_resp
        else:
            datasourceDict = getDatasourceInfo(datasource_id, component, domain, app)
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

            es_resp = es.es_alarmapi(post_data)
            res_dict['data'] = es_resp

        return Response(res_dict, http_status.HTTP_200_OK)



class GatePassView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        domain = query_params.get('domain', None)
        component = query_params.get('component', None)
        condition_sql = ' where 1=1 '
        params = []
        if domain:
            condition_sql += ' and (`domain`=%s) '
            params.extend([domain])
        if component:
            condition_sql += ' and (`component`=%s) '
            params.extend([component])
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(`component`,%s) or instr(domain,%s)  or instr(uri,%s) or instr(note,%s)) '
            params.extend([searchVal] * 4)

        res_dict = get_func('id', query_params, condition_sql, params, 'l_gatepass', selfields="*", camel=False)

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        domain = request_data.get('domain','')
        request_data['domain'] = domain.strip()
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        resp = put_func('id', request_data, GatePass, GatePasser)
        if domain:
            try:
                r = RedisClient('dbmonitor').client
                del_keys = r.keys(f'gatefilter:{domain}_*')
                r.delete(*del_keys)
            except Exception as e:
                logger.warning(f'del gatefilter err:{e}')
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data

        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]

        resp = delete_func('id', deleteIds, GatePass)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys(f'gatefilter:*')
            r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del gatefilter err:{e}')
        return Response(resp, http_status.HTTP_200_OK)


class AppPassView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        app = query_params.get('app', None)
        component = query_params.get('component', None)
        condition_sql = ' where 1=1 '
        params = []
        if app:
            condition_sql += ' and (`app`=%s) '
            params.extend([app])
        if component:
            condition_sql += ' and (`component`=%s) '
            params.extend([component])
        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(`component`,%s) or instr(app,%s)  or instr(uri,%s) or instr(note,%s)) '
            params.extend([searchVal] * 4)

        res_dict = get_func('id', query_params, condition_sql, params, 'l_apppass', selfields="*", camel=False)

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        request_data = request.data
        app = request_data.get('app', '')
        request_data['app'] = app.strip()
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"updated_by:{login_user},request.data:{request.data}")
        resp = put_func('id', request_data, AppPass, AppPasser)
        if app:
            try:
                r = RedisClient('dbmonitor').client
                del_keys = r.keys(f'appfilter:{app}_*')
                r.delete(*del_keys)
            except Exception as e:
                logger.warning(f'del appfilter err:{e}')
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        login_user = request.username if hasattr(request, 'username') else 'sys'
        logger.info(f"delete by:{login_user},params:{query_params}")
        deleteIds = query_params.get('deleteIds', [])
        if not deleteIds:
            deleteIds = [query_params['id']]

        resp = delete_func('id', deleteIds, AppPass)
        try:
            r = RedisClient('dbmonitor').client
            del_keys = r.keys(f'appfilter:*')
            r.delete(*del_keys)
        except Exception as e:
            logger.warning(f'del appfilter err:{e}')
        return Response(resp, http_status.HTTP_200_OK)




class GateFilterView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [], 'count': 0}
        resp_data = get_gate_filter(query_params)
        resp_data_valid = []
        for item in resp_data:
            end_time = item.get('end_time','')
            if not end_time:
                resp_data_valid.append(item.get('uri'))
            if end_time:
                now_date = int(time.time())
                flag_add = True
                try:
                    if len(str(end_time)) < 11:
                        endtime_stamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d')))
                    else:
                        endtime_stamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S')))
                    if now_date > endtime_stamp:
                        flag_add = False
                except:pass
                if flag_add:
                    resp_data_valid.append(item.get('uri'))
        res_dict['data'] = resp_data_valid
        res_dict['count'] = len(resp_data_valid)
        return Response(res_dict, http_status.HTTP_200_OK)


class AppFilterView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        res_dict = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [], 'count': 0}
        resp_data = get_app_filter(query_params)
        resp_data_valid = []
        for item in resp_data:
            end_time = item.get('end_time','')
            if not end_time:
                resp_data_valid.append(item.get('uri'))
            if end_time:
                now_date = int(time.time())
                flag_add = True
                try:
                    if len(str(end_time)) < 11:
                        endtime_stamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d')))
                    else:
                        endtime_stamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S')))
                    if now_date > endtime_stamp:
                        flag_add = False
                except:pass
                if flag_add:
                    resp_data_valid.append(item.get('uri'))
        res_dict['data'] = resp_data_valid
        res_dict['count'] = len(resp_data_valid)
        return Response(res_dict, http_status.HTTP_200_OK)