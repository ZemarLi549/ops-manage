from django.conf import settings
import redis
import functools
import json
from apps.management.models import User,OpsToken
from apps.common.dbopr import get_func
from apps.om_logsearch.models import DataSource,ComponentIndex
from apps.common.dbopr import dict_query
import logging
import uuid
logger = logging.getLogger(__name__)

class RedisClient(object):
    def __init__(self, dbtype,decode_responses=None):
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.password = settings.REDIS_PASSWORD
        if dbtype == 'dblog':
            self.db = 2
        elif dbtype == 'dbproject':
            self.db = 3
        elif dbtype == 'dbmonitor':
            self.db = 4
        elif dbtype == 'dbalarm':
            self.db = 5
        if decode_responses:
            self.pool = redis.ConnectionPool(host=self.host, port=int(self.port), db=self.db, password=self.password,
                                             socket_connect_timeout=1, decode_responses=True)
        else:
            self.pool = redis.ConnectionPool(host=self.host, port=int(self.port), db=self.db, password=self.password,
                                             socket_connect_timeout=1)

    @property
    def client(self):
        return redis.Redis(connection_pool=self.pool)
# 加锁
def acquire_lock_once(lock_name, acquire_timeout=1800, lock_timeout=30):
    """
    param lock_name: 锁名称
    param acquire_timeout: 客户端获取锁的超时时间
    param lock_timeout: 锁过期时间, 超过这个时间锁自动释放
    """
    redis_cli = RedisClient('dbalarm',decode_responses=True).client
    identifier = str(uuid.uuid4())
    # redis_cli.delete(lock_name)# 备用

    # end_time = time.time() + acquire_timeout   # 客户端获取锁的结束时间
    # while time.time() <= end_time:
    # setnx(key, value) 只有 key 不存在情况下将 key 设置为 value 返回 True
    # 若 key 存在则不做任何动作,返回 False
    if redis_cli.setnx(lock_name, identifier):
        redis_cli.expire(lock_name, lock_timeout)   # 设置锁的过期时间，防止线程获取锁后崩溃导致死锁
        return identifier   # 返回锁唯一标识
    elif redis_cli.ttl(lock_name) == -1:   # 当锁未被设置过期时间时，重新设置其过期时间
        redis_cli.expire(lock_name, lock_timeout)
        # time.sleep(0.001)
    return False   # 获取超时返回 False


# 释放锁
def release_lock(lock_name, identifier):
    """
    param lock_name:   锁名称
    param identifier:  锁标识
    """
    redis_cli = RedisClient('dbalarm',decode_responses=True).client
    # 解锁操作需要在一个 redis 事务中进行，python 中 redis 事务通过 pipeline 封装实现
    with redis_cli.pipeline() as pipe:
        while True:
            try:
                # 使用 WATCH 监听锁，如果删除过程中锁自动失效又被其他客户端拿到，即锁标识被其他客户端修改
                # 此时设置了 WATCH 事务就不会再执行，这样就不会出现删除了其他客户端锁的情况
                pipe.watch(lock_name)
                id = pipe.get(lock_name)
                if id and id == identifier:   # 判断解锁与加锁线程是否一致
                    pipe.multi()
                    pipe.delete(lock_name)   # 标识相同，在事务中删除锁
                    pipe.execute()    # 执行EXEC命令后自动执行UNWATCH
                    return True
                pipe.unwatch()
                break
            except redis.WatchError:
                pass
        return False
def redis_cache(schema):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if schema == 'get_code_ls':
                username = args[0]
                try:
                    r = RedisClient('dbmonitor').client
                    rk = f'getcode:{username}'
                    if not r.exists(rk):
                        resp_ = func(*args, **kwargs)
                        r.set(rk, json.dumps(resp_), ex=60 * 60*6)
                        logger.info(f'user:{username},code not exsits set over')
                        return resp_
                    else:
                        # logger.info(f'user:{username},get code from redis')
                        resp_ = json.loads(r.get(rk))
                        return resp_
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_all_code_ls':
                try:
                    r = RedisClient('dbmonitor').client
                    rk = f'allcode'
                    if not r.exists(rk):
                        resp_ = func(*args, **kwargs)
                        r.set(rk, json.dumps(resp_), ex=60 * 60*24)
                        logger.info(f'allcode not exsits set over')
                        return resp_
                    else:
                        resp_ = json.loads(r.get(rk))
                        # logger.info(f'allcode exsits')
                        return resp_
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_token_ls':
                try:
                    token = args[0]
                    if token:
                        r = RedisClient('dbmonitor').client
                        rk = f'token:{token}'
                        if not r.exists(rk):
                            resp_ = func(*args, **kwargs)
                            r.set(rk, json.dumps(resp_), ex=60 * 60*24)
                            logger.info(f'get_token_ls not exsits set over')
                            return resp_
                        else:
                            resp_ = json.loads(r.get(rk))
                            logger.info(f'get_token_ls exsits')
                            return resp_
                    else:
                        return []
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_gate_filter':
                query_params = args[0]
                domain = query_params.get('domain', '')
                component = query_params.get('component', '')
                if component and '|' in component:
                    compo_ls = component.split('|')
                    component = compo_ls[-1]

                try:
                    r = RedisClient('dbmonitor').client
                    rk = f'gatefilter:{domain}_{component}_end'
                    if not r.exists(rk):
                        resp_ = func(*args, **kwargs)
                        r.set(rk, json.dumps(resp_), ex=60 * 60*8)
                        logger.info(f'filter:{domain}_{component},code not exsits set over')
                        return resp_
                    else:
                        # logger.info(f'user:{username},get code from redis')
                        resp_ = json.loads(r.get(rk))
                        return resp_
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_app_filter':
                query_params = args[0]
                app = query_params.get('app', '')
                component = query_params.get('component', '')
                if component and '|' in component:
                    compo_ls = component.split('|')
                    component = compo_ls[-1]
                try:
                    r = RedisClient('dbmonitor').client
                    rk = f'appfilter:{app}_{component}_end'
                    if not r.exists(rk):
                        resp_ = func(*args, **kwargs)
                        r.set(rk, json.dumps(resp_), ex=60 * 60*7)
                        logger.info(f'filter:{app}_{component},code not exsits set over')
                        return resp_
                    else:
                        # logger.info(f'user:{username},get code from redis')
                        resp_ = json.loads(r.get(rk))
                        return resp_
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_datasource_info':
                datasource_id,component,domain,app = args
                if datasource_id:
                    rk = f'getsource_id:{datasource_id}'
                elif domain and component:
                    rk = f'getsource_domain:{domain}_{component}'
                elif app and component:
                    rk = f'getsource_app:{app}_{component}'
                elif component:
                    rk = f'getsource_comp:{component}'
                else:
                    resp_ = func(*args, **kwargs)
                    return resp_
                try:
                    r = RedisClient('dbmonitor').client

                    if not r.exists(rk):
                        resp_ = func(*args, **kwargs)
                        r.set(rk, json.dumps(resp_), ex=60 * 60*24)
                        logger.info(f'filter:{rk},code not exsits set over')
                        return resp_
                    else:
                        # logger.info(f'user:{username},get code from redis')
                        resp_ = json.loads(r.get(rk))
                        return resp_
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_comp_info':
                component, source = args
                rk = f'getcomp:{component}_{source}'

                try:
                    r = RedisClient('dbmonitor').client
                    if not r.exists(rk):
                        resp_ = func(*args, **kwargs)
                        r.set(rk, json.dumps(resp_), ex=60 * 60 * 25)
                        logger.info(f'filter:{rk},code not exsits set over')
                        return resp_
                    else:
                        # logger.info(f'user:{username},get code from redis')
                        resp_ = json.loads(r.get(rk))
                        return resp_
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_all_black':
                try:
                    r = RedisClient('dbalarm').client
                    rk = f'alarm_black:all'
                    if not r.exists(rk):
                        resp_ = func(*args, **kwargs)
                        r.set(rk, json.dumps(resp_), ex=60 * 60*24*30)
                        logger.info(f'alarm_black:all not exsits set over')
                        return resp_
                    else:
                        resp_ = json.loads(r.get(rk))
                        # logger.info(f'alarm_config exsits')
                        return resp_
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_alarm_id':
                try:
                    alarm_id = args[0]
                    if alarm_id:
                        r = RedisClient('dbalarm').client
                        rk = f'alarm_config:{alarm_id}'
                        if not r.exists(rk):
                            resp_ = func(*args, **kwargs)
                            r.set(rk, json.dumps(resp_), ex=60 * 60*24*30)
                            logger.info(f'alarm_config not exsits set over')
                            return resp_
                        else:
                            resp_ = json.loads(r.get(rk))
                            # logger.info(f'alarm_config exsits')
                            return resp_
                    else:
                        return []
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator



@redis_cache('get_token_ls')
def get_token_ls(token):
    code_ls = []
    try:
        # get_res_sql = f"select distinct opstoken.token from opstoken where role_id in (select role_id  from om_resource_role  where resource_id in (select id from om_resource where `code` in {sql_str}));"
        get_res_sql = f"select distinct om_resource.code from om_resource inner join om_resource_role on om_resource.id = om_resource_role.resource_id and om_resource_role.role_id in (select role_id from opstoken where token='{token}');"
        res_list = dict_query(get_res_sql, [])
        code_ls = [item.get('code') for item in res_list]

    except Exception as e:
        logger.error(e)
    return code_ls

def set_identity_json(identity,json_info,expire_time=None,prefix = 'alarm_zhiwen'):
    if identity:
        rk = f'{prefix}:{identity}'
        try:
            r = RedisClient('dbalarm').client
            if not expire_time:
                r.set(rk, json.dumps(json_info))
            else:
                r.set(rk, json.dumps(json_info), ex=expire_time)
        except Exception as e:
            logger.error(f'set redis set_identity_json err:{e}')
def has_identity_json(identity,prefix = 'alarm_zhiwen'):
    resp_ = None
    if identity:
        rk = f'{prefix}:{identity}'
        try:
            r = RedisClient('dbalarm').client
            if r.exists(rk):
                resp_ = json.loads(r.get(rk))
        except Exception as e:
            logger.error(f'get redis identity key err:{e}')
    return resp_
@redis_cache('get_code_ls')
def get_code_ls(username):
    code_ls = []
    menu_set = set()
    try:
        user_obj = User.objects.get(name=username)
        user_id = user_obj.id
        dept_power = user_obj.dept_power
        department_id = user_obj.department_id
        get_res_sql = f'select a.id,a.parent_id,a.router,a.perms,a.type,a.view_path,a.keepalive,a.is_show,a.name,a.icon,a.order_num from om_resource a  inner join om_resource_role b on a.id = b.menu_id and b.role_id in (select role_id from om_user_role where user_id={user_id}) '
        res_list = dict_query(get_res_sql, [])
        if dept_power:
            get_res_sql_dept = f'select a.id,a.parent_id,a.router,a.perms,a.type,a.view_path,a.keepalive,a.is_show,a.name,a.icon,a.order_num from om_resource a  inner join om_resource_role b on a.id = b.menu_id and b.role_id in (select role_id from om_dept_role where department_id={department_id}) '
            res_list_dept = dict_query(get_res_sql_dept, [])
            res_list.extend(res_list_dept)
        for menu in res_list:
            id_ = menu['id']
            if not id_ in menu_set:
                code_ls.append(menu)
                menu_set.add(id_)
    except Exception as e:
        logger.error(e)
    return code_ls

@redis_cache('get_all_code_ls')
def get_all_code_ls():
    get_res_sql = f'select distinct om_resource.code from om_resource where res_type="api"'
    res_list = dict_query(get_res_sql, [])
    code_ls = []
    for code in res_list:
        code_ls.append(code.get('code'))
    return code_ls

@redis_cache('get_alarm_id')
def get_alarm_id(alarm_id):
    get_res_sql = f'select `id`,rule_name,alarm_to,alert_start,alert_end,`name`,send_type,label_name,label_send from alarm_config where id=%s'
    res_list = dict_query(get_res_sql, [int(alarm_id)],camel=False)

    alarm_dict ={}
    if res_list:
        alarm_dict = res_list[0]
        alarm_dict['alarm_to'] = json.loads(alarm_dict.get('alarm_to',"{}"))
        alarm_dict['label_send'] = json.loads(alarm_dict.get('label_send',"{}"))
    return alarm_dict


def verify_power(request):
    # check power to op
    flag_ = False
    POWER_DICT = {
        "GET": 'get',
        "PUT": 'put',
        "POST": 'post',
        "DELETE": 'del',
        "OPTION": 'option',
    }
    try:
        username = request.username
        method = request.method
        path = request.path_info.replace('/ops-management/v1/', '')
        code_now = 'backapi.' + path + '/' + POWER_DICT.get(method, 'view')
        all_code = get_all_code_ls()
        if code_now in all_code:
            code_ls = get_code_ls(username)
            if not code_now in code_ls:
                logger.error(str(username)+':no power')
                flag_ = True
                code_now = code_now
    except:
        #login api
        code_now ='login'

    return flag_,code_now


@redis_cache('get_gate_filter')
def get_gate_filter(query_params):
    domain = query_params.get('domain', '')
    component = query_params.get('component', '')
    if component and '|' in component:
        compo_ls = component.split('|')
        component = compo_ls[-1]
    condition_sql = ' where 1=1 '
    params = []
    if domain:
        condition_sql += ' and (`domain`=%s or `domain`="all") '
        params.extend([domain])
    if component:
        condition_sql += ' and (`component`=%s or `component`="all") '
        params.extend([component])

    res_dict = get_func('id', query_params, condition_sql, params, 'l_gatepass', selfields="uri,end_time", camel=False)
    return res_dict['data']

@redis_cache('get_app_filter')
def get_app_filter(query_params):
    app = query_params.get('app', '')
    component = query_params.get('component', '')
    if component and '|' in component:
        compo_ls = component.split('|')
        component = compo_ls[-1]
    condition_sql = ' where 1=1 '
    params = []
    if app:
        condition_sql += ' and (`app`=%s or `app`="all") '
        params.extend([app])
    if component:
        condition_sql += ' and (`component`=%s or `component`="all") '
        params.extend([component])

    res_dict = get_func('id', query_params, condition_sql, params, 'l_apppass', selfields="uri,end_time", camel=False)
    return res_dict['data']
@redis_cache('get_datasource_info')
def getDatasourceInfo(datasource_id,component,domain,app):
    datasourceDict = {
        'source' : 'es',
        'es_host': '',
        'es_username' :'',
        'es_pwd' :'',
        'project_name' : '',
        'logstore' :'',
        'region' : '',
        'alisecret' :'',
        'alikey' : ''
    }

    if datasource_id:
        datasource_list = DataSource.objects.filter(id=int(datasource_id)).values('source','host','username',
                                                                                  'password','project_name','logstore',
                                                                                  'region','alisecret','alikey')
        if datasource_list:
            datasourceDict = datasource_list[0]
        else:
            raise Exception(f'datasource_id:{datasource_id} no datasource')
    elif domain and component:
        sql_datasource = f" select b.* from l_gateconfig a right join l_datasource b on a.datasource_id=b.id where a.domain=%s and a.component=%s "
        datasource_list = dict_query(sql_datasource, [domain, component], camel=False)
        if datasource_list:
            datasourceDict = datasource_list[0]
        else:
            raise Exception(f'domain:{domain},component:{component} no datasource')
    elif app and component:
        sql_datasource = f" select b.* from l_appconfig a right join l_datasource b on a.datasource_id=b.id where a.app=%s and a.component=%s "
        datasource_list = dict_query(sql_datasource, [app, component], camel=False)
        if datasource_list:
            datasourceDict = datasource_list[0]
        else:
            raise Exception(f'domain:{domain},component:{component} no datasource')
    elif component:
        sql_datasource = f" select b.* from l_component a right join l_datasource b on a.datasource_id=b.id where  a.component=%s "
        datasource_list = dict_query(sql_datasource, [component], camel=False)
        if datasource_list:
            datasourceDict = datasource_list[0]
        else:
            raise Exception(f'domain:{domain},component:{component} no datasource')
    return datasourceDict


@redis_cache('get_comp_info')
def getComponentInfo(component,source):
    componentDict = {}
    componentObjList = ComponentIndex.objects.filter(component=component, source=source).values('component','index_str',
                                                                                                'time_field','field_type',
                                                                                                'source','datasource_id')
    if componentObjList:
        componentDict = componentObjList[0]
    return componentDict

@redis_cache('get_all_black')
def get_all_black():
    get_res_sql = f'select `rule_re`,`black_to` from alarm_black'
    res_list = dict_query(get_res_sql, [],camel=False)
    return res_list