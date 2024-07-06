
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from apps.common.renderers import MyJSONRenderer
from .serializers import *
from django.conf import settings
from apps.common.try_catch import try_catch,power_decorator
from .models import *
from .forms import *
from apps.common.tools import Execution
from apps.common.tools import encrypt
from apps.common.dbopr import dict_query
from apps.common.redisclient import get_code_ls,RedisClient
from apps.common.dbopr import get_func,put_func,delete_func,to_underline,get_relative_func
from datetime import datetime,date
import decimal
import logging
logger = logging.getLogger(__name__)

# from drf_yasg import openapi

# Create your views here.
class UserInfoView(APIView):
    """
    """

    @try_catch
    def get(self, request):

        data = dict_query(f'select * from om_user where name=%s',[request.username])[0]

        data['loginIp'] = request.loginIp

        return Response({'code': 200, 'message': 'OK', 'data': data},
                        http_status.HTTP_200_OK)


class SearchUserInfoView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        userId = query_params['userId']
        user_query_sql = 'select a.*, b.name as departmentName,GROUP_CONCAT(c.role_id) as roles,GROUP_CONCAT(d.role_id) as deptRoles from om_user a left join om_dept b on a.department_id =b.id left join om_user_role c  on a.id = c.user_id  left join om_dept_role d  on b.id = d.department_id'
        condition_sql = ' where a.id is not NUll '
        params = []

        if userId:
            condition_sql += ' and (a.id = %s) '
            params.append("{}".format(userId))

        data = dict_query(user_query_sql + condition_sql,[*params])[0]

        data['roles'] = [int(roleid) for roleid in set(data['roles'].split(',') if data['roles'] else [])]

        data['deptRoles'] = [int(roleid) for roleid in set(data['deptRoles'].split(',') if data['deptRoles'] else [])]
        return Response({'code': 200, 'message': 'OK', 'data': data},
                        http_status.HTTP_200_OK)

class UserPermView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        data = {}
        username = request.username
        perms = []
        menu_all = get_code_ls(username)
        data['menus'] = menu_all
        for item in menu_all:
            if item['type'] == 2:
                perms.append(item['perms'])
        data['perms'] = perms



        return Response({'code': 200, 'message': 'OK', 'data': data},
                        http_status.HTTP_200_OK)

class UserView(APIView):
    """
    """


    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        searchVal = query_params.get('searchVal', None)
        status = query_params.get('status', None)
        deptIds = query_params.get('deptIds', None)
        page = int(query_params.get('page', '1'))
        size = int(query_params.get('size', '10'))

        if page <= 0 or size <= 0 or size > 5000:
            raise ValueError(f'page{page} or size{size} is not in valid range.')

        user_query_sql = 'select a.*, b.name as departmentName,GROUP_CONCAT(d.name) as roleNames from om_user a left join om_dept b on a.department_id =b.id left join om_user_role c  on a.id = c.user_id left join om_role d on d.id=c.role_id '
        condition_sql = ' where 1=1 '
        params = []

        if searchVal:
            searchVal = searchVal.strip()
            condition_sql += ' and (instr(a.name,%s) or instr(a.realname,%s) or instr(a.phone,%s) or instr(a.remark,%s) or instr(d.name,%s)) '
            params.extend([searchVal] * 5)
        if status:
            status = status.replace('"', '').replace("'", '')
            condition_sql += f' and a.status in ({status}) '
        if deptIds:
            deptIds = deptIds.replace('"', '').replace("'", '')
            condition_sql += f' and b.id in ({deptIds}) '



        obj_id_query_sql = f'select a.id from om_user a left join om_dept b on a.department_id =b.id left join om_user_role c  on a.id = c.user_id left join om_role d on d.id=c.role_id'
        total_cnt = dict_query("select count(1) cnt from ( " + obj_id_query_sql + condition_sql + " ) a ",params,camel=False)[0]['cnt']
        if total_cnt == 0:
            dict_ = {'status': 'success', 'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': [], 'count': total_cnt}
            return Response(dict_, http_status.HTTP_200_OK)

        user_list = dict_query(user_query_sql + condition_sql + 'group by a.id order by a.updated_at desc limit %s,%s',
                                  [*params, (page - 1) * size, size])

        if not user_list:
            return Response({'code': 200, 'message': 'OK', 'data': [], },
                            http_status.HTTP_200_OK)

        for item in user_list:
            item['roleNames'] = [name for name in set(item['roleNames'].split(',') if item['roleNames'] else [])]
        return Response({'code': 200, 'message': 'OK', 'data': user_list,'count': total_cnt},
                        http_status.HTTP_200_OK)

    @try_catch
    def post(self, request):
        logger.info("request.data:%s", request.data)
        name = request.data.get('name', None)
        realname = request.data.get('realname', '')
        password = request.data.get('password', 'ops_manage')
        login_user = request.data.get('login_user', 'sys')
        status = request.data.get('status', 1)
        if not name:
            raise KeyError('name missing in request.')

        if not User.objects.filter(name=name).exists():
            User.objects.create(name=name,
                                password=encrypt(password,settings.RELEASE_KEY),
                                realname=realname,
                                status=status,
                                created_by=login_user)
            return Response({'code': 200, 'message': 'OK'},
                            http_status.HTTP_200_OK)
        else:
            logger.error("user(%s) alread exists.", name)
            return Response({'code': 500, 'message': f"user({name}) already exists."},
                            http_status.HTTP_500_INTERNAL_SERVER_ERROR)


    @try_catch
    @power_decorator(['sys:user:update'])
    def put(self, request):
        logger.info("request.data:%s", request.data)
        request_data = request.data
        request_data = to_underline(request_data)
        if 'password' in request_data.keys():
            if 'name' in request_data.keys():
                dict_ = {'name': request_data.get('name','')}
                obj = User.objects.filter(**dict_).first()
                request_data['id'] = obj.id
            request_data['password'] = encrypt(request_data['password'],settings.RELEASE_KEY)
        login_user = request.username if hasattr(request, 'username') else 'sys'
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, User, Userer)
        roles = request_data.get('roles',[])
        user_id = resp['data']

        if 'roles' in request_data.keys():
            put_relate(User_Role,roles, 'role_id', 'user_id', user_id)
        r = RedisClient('dbmonitor').client
        username = User.objects.get(id=user_id).name
        r.delete(f'getcode:{username}')

        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    @power_decorator(['sys:user:delete'])
    def delete(self, request):
        query_params = request.data
        logger.info("params:%s", query_params)
        userIds = query_params.get('userIds', [])
        if not userIds:
            userIds = [query_params['id']]
        #删除关联
        for user_id in userIds:
            if User.objects.filter(id=user_id).exists():
                ex = Execution()
                funcs = ex.load_plugins("management", "models", "User")
                for table, table_obj in funcs.items():
                    try:
                        table_obj.objects.filter(user_id=user_id).delete()
                    except Exception as e:
                        logger.error(f'{table} del error:{e}')
        resp = delete_func('id', userIds, User)

        return Response(resp, http_status.HTTP_200_OK)

class RoleInfoView(APIView):
    """
    """

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        role_id = query_params.get('roleId','')
        if not role_id:
            raise Exception('role_id null')
        query_sql = 'select * from om_resource_role'
        params = []
        condition_sql = ' where  1=1 '
        if role_id:
            condition_sql += ' and (role_id = %s) '
            params.append("{}".format(role_id))
        menu_list  = dict_query(query_sql + condition_sql + ' order by updated_at desc, id desc',[*params])


        query_sql = 'select * from om_dept_role'
        dept_list  = dict_query(query_sql + condition_sql + ' order by updated_at desc, id desc',[*params])

        roleInfo = dict_query(f'select * from om_role where `id`="{role_id}"')[0]
        res_dict = {'code': http_status.HTTP_200_OK, 'message': 'OK', 'data': {'menus':menu_list,'depts':dept_list,'roleInfo':roleInfo}}
        return Response(res_dict, http_status.HTTP_200_OK)


#menus,'menu_id','role_id',role_id
def put_relate(model_obj,new_list,new_fid,main_fid,main_id):
    dict_main = {main_fid:main_id}
    obj_ids_new = set(new_list)
    obj_ids_ls = [
        item.get(new_fid) for item in model_obj.objects.filter(
            **dict_main).values(new_fid)
    ]
    obj_ids_old = set(obj_ids_ls)
    obj_ids_new = set(
        [int(item) if item else 0 for item in obj_ids_new])
    obj_ids_old = set(
        [int(item) if item else 0 for item in obj_ids_old])
    obj_create_set = obj_ids_new.difference(obj_ids_old)
    obj_del_set = obj_ids_old.difference(obj_ids_new)


    list_to_insert = list()
    for menu_id in list(obj_create_set):
        dict_ = {new_fid:int(menu_id),main_fid:main_id}
        list_to_insert.append(model_obj(**dict_))
    if list_to_insert:
        model_obj.objects.bulk_create(list_to_insert)

    del_dict = {new_fid+'__in':list(obj_del_set)}
    model_obj.objects.filter(**del_dict).delete()

class RoleView(APIView):
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
            condition_sql += ' and (instr(`name`,%s) or instr(description,%s)) '
            params.extend([searchVal] * 2)
        res_dict = get_func('id', query_params, condition_sql, params, 'om_role', selfields="*")

        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        logger.info("request.data:%s", request.data)
        request_data = request.data
        request_data = to_underline(request_data)
        login_user = request.username if hasattr(request, 'username') else 'sys'
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, Role, Roleer)
        role_id = resp['data']


        menus = request_data.get('menus',[])
        depts = request_data.get('depts',[])

        put_relate(Resource_Role,menus,'menu_id','role_id',role_id)

        put_relate(Department_Role,depts, 'department_id', 'role_id', role_id)
        r = RedisClient('dbmonitor').client
        del_keys = r.keys('getcode:*')
        if del_keys:
            r.delete(*del_keys)

        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        logger.info("params:%s", query_params)
        roleIds = query_params.get('roleIds',[])
        if not roleIds:
            roleIds = [query_params['id']]



        for role_id in roleIds:
            if Role.objects.filter(id=role_id).exists():
                ex = Execution()
                funcs = ex.load_plugins("management", "models", "Role")
                for table, table_obj in funcs.items():
                    try:
                        table_obj.objects.filter(role_id=role_id).delete()
                    except Exception as e:
                        logger.error(f'{table} del error:{e}')

        r = RedisClient('dbmonitor').client
        del_keys = r.keys('getcode:*')
        if del_keys:
            r.delete(*del_keys)

        resp = delete_func('id', roleIds, Role)
        return Response(resp, http_status.HTTP_200_OK)


class ResourceView(APIView):
    """
    """
    # schema =  ResourceViewSchema()
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        params = []
        condition_sql = ' where  1=1  '
        res_dict = get_func('id', query_params, condition_sql, params, 'om_resource', selfields="*")
        for item in res_dict['data']:
            for key_, val_ in item.items():
                if key_ in ['keepalive', 'isShow']:
                    item[key_] = True if val_ else False
        return Response(res_dict, http_status.HTTP_200_OK)


    @try_catch
    def put(self, request):
        logger.info("request.data:%s", request.data)
        request_data = request.data
        request_data = to_underline(request_data)
        parent_id = int(request_data.get('parent_id', -1))
        if parent_id <= 0:
            request_data['parent_id'] = None
        login_user = request.username if hasattr(request, 'username') else 'sys'
        request_data['updated_by'] = login_user

        resp = put_func('id', request_data, Resource, Resourceer,check_name=False)
        if resp.get('is_new'):
            menu_id = resp['data']
            admin_id = Role.objects.filter(name='#超级管理员#').first().id
            Resource_Role.objects.create(role_id=admin_id,menu_id=menu_id)
        r = RedisClient('dbmonitor').client
        del_keys = r.keys('getcode:*')
        if del_keys:
            r.delete(*del_keys)
        return Response(resp, http_status.HTTP_200_OK)


    @try_catch
    def delete(self, request):
        query_params = request.data
        logger.info("params:%s", query_params)
        resource_id = query_params.get('id', None)

        if not resource_id:
            raise KeyError('resource_id missing in request.')
        resource_id = int(resource_id)

        if Resource.objects.filter(id=resource_id).exists():
            ex = Execution()
            funcs = ex.load_plugins("management", "models", "Resource")
            for table, table_obj in funcs.items():
                try:
                    table_obj.objects.filter(menu_id=resource_id).delete()
                except Exception as e:
                        logger.error(f'{table} del error:{e}')

            Resource.objects.filter(id=resource_id).delete()
            Resource.objects.filter(parent_id=resource_id).delete()

            r = RedisClient('dbmonitor').client
            del_keys = r.keys('getcode:*')
            if del_keys:
                r.delete(*del_keys)
            return Response({'code': 200, 'message': 'OK'},
                            http_status.HTTP_200_OK)
        else:
            logger.error("resource(%d) does not exist.", resource_id)
            return Response({'code': 500, 'message': f"resource({resource_id}) does not exist."},
                            http_status.HTTP_200_OK)




def convert_id(query_params):
    query_params_pro = {}
    for key, val in query_params.items():
        if 'Id' or 'id' in key:
            key = 'id'
        query_params_pro[key] = val
    return query_params_pro
class DepartmentView(APIView):
    """
    """
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        query_params = request.query_params.dict()
        logger.info("params:%s", query_params)
        params = []
        condition_sql = ' where 1=1 '
        res_dict = get_func('id', query_params, condition_sql, params, 'om_dept',selfields="*")


        return Response(res_dict, http_status.HTTP_200_OK)

    @try_catch
    def put(self, request):
        logger.info("request.data:%s", request.data)
        request_data = request.data
        request_data = to_underline(request_data)
        parent_id = int(request_data.get('parent_id',-1))
        if parent_id<=0:
            request_data['parent_id'] = None
        login_user = request.username if hasattr(request, 'username') else 'sys'
        request_data['updated_by'] = login_user
        resp = put_func('id', request_data, Department, Departmenter)
        return Response(resp, http_status.HTTP_200_OK)

    @try_catch
    def delete(self, request):
        query_params = request.data
        logger.info("params:%s", query_params)
        department_id = query_params.get('id','')
        Department_Role.objects.filter(department_id=department_id).delete()
        resp = delete_func('id', query_params.get('id',''), Department)
        resp = delete_func('parent_id', query_params.get('id',''), Department)
        return Response(resp, http_status.HTTP_200_OK)
