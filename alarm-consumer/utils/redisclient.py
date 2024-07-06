from ops_alarm import settings
import redis
import functools
import json
import time
import uuid
from utils.dbtool import MysqlOp
from utils.logger import logger
class RedisClient(object):
    def __init__(self, dbtype,decode_responses=None):
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.password = settings.REDIS_PASSWORD
        # is_redis_cluster = settings.IS_REDIS_CLUSTER
        # if is_redis_cluster=='1':
        #     self.db = 0
        # else:
        if dbtype == 'dblog':
            self.db = 2
        elif dbtype == 'dbproject':
            self.db = 3
        elif dbtype == 'dbmonitor':
            self.db = 4
        elif dbtype == 'dbalarm':
            self.db = 5
        if decode_responses:
            self.pool = redis.ConnectionPool(host=self.host, port=int(self.port), db=self.db, password=self.password,socket_connect_timeout=1,decode_responses=True)
        else:
            self.pool = redis.ConnectionPool(host=self.host, port=int(self.port), db=self.db, password=self.password,socket_connect_timeout=1)

    @property
    def client(self):
        return redis.Redis(connection_pool=self.pool)

def has_identity_key(identity,prefix = 'alarm_identity'):
    has_flag = False
    if identity:
        rk = f'{prefix}:{identity}'
        try:
            r = RedisClient('dbalarm').client
            if r.exists(rk):
                has_flag = True
        except Exception as e:
            logger.error(f'get redis identity key err:{e}')
    return has_flag


def set_identity_key(identity,expire_time,prefix = 'alarm_identity'):
    if identity:
        rk = f'{prefix}:{identity}'
        try:
            r = RedisClient('dbalarm').client
            r.set(rk, 1, ex=expire_time)
        except Exception as e:
            logger.error(f'set redis set_identity_json err:{e}')

#高并发锁
def set_status_key(identity,status=1,expire_time=600,prefix = 'mysqldeploy'):
    if identity:
        rk = f'{prefix}:{identity}'
        try:
            r = RedisClient('dbalarm').client
            if not expire_time:
                r.set(rk, status)
            else:
                r.set(rk, status, ex=expire_time)
        except Exception as e:
            logger.error(f'set redis set_status_key err:{e}')

#高并发锁
def has_status_key(identity,prefix = 'mysqldeploy'):
    status = None
    if identity:
        rk = f'{prefix}:{identity}'
        try:
            r = RedisClient('dbalarm').client
            if r.exists(rk):
                status = int(r.get(rk).decode('utf-8'))
        except Exception as e:
            logger.error(f'get redis has_status_key err:{e}')
    return status

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
def redis_cache(schema):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if schema == 'get_alarm_id':
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
            elif schema == 'get_user_info':
                try:
                    username = args[0]
                    if username:
                        r = RedisClient('dbalarm').client
                        rk = f'alarm_user:{username}'
                        if not r.exists(rk):
                            resp_ = func(*args, **kwargs)
                            r.set(rk, json.dumps(resp_), ex=60 * 60*24*58)
                            logger.info(f'alarm_user not exsits set over')
                            return resp_
                        else:
                            resp_ = json.loads(r.get(rk))
                            logger.debug(f'alarm_user exsits:{resp_}')
                            return resp_
                    else:
                        return []
                except Exception as e:
                    logger.error(e)
                    resp_ = func(*args, **kwargs)
                    return resp_
            elif schema == 'get_rule_info':
                try:
                    name = args[0]
                    if name:
                        r = RedisClient('dbalarm').client
                        rk = f'alarm_rule:{name}'
                        if not r.exists(rk):
                            resp_ = func(*args, **kwargs)
                            r.set(rk, json.dumps(resp_), ex=60 * 60*24*17)
                            logger.info(f'alarm_rule not exsits set over')
                            return resp_
                        else:
                            resp_ = json.loads(r.get(rk))
                            logger.debug(f'alarm_config exsits')
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




@redis_cache('get_alarm_id')
def get_alarm_id(alarm_id):
    get_res_sql = f'select `id`,rule_name,alarm_to,alert_start,alert_end from alarm_config where id=%s'
    res_list = MysqlOp().mysql_dict_query(get_res_sql, [alarm_id])

    alarm_dict ={}
    if res_list:
        alarm_dict = res_list[0]
        alarm_dict['alarm_to'] = json.loads(alarm_dict.get('alarm_to',"{}"))
    return alarm_dict


@redis_cache('get_user_info')
def get_user_info(username):
    get_res_sql = f'select `name`,`phone`,`email`,`username` from alarm_user where username=%s'
    res_list = MysqlOp().mysql_dict_query(get_res_sql, [username])
    alarm_dict ={}
    if res_list:
        alarm_dict = res_list[0]
    return alarm_dict

@redis_cache('get_rule_info')
def get_rule_info(name):
    get_res_sql = f'select `name`,`rule_keys`,`rule_re`,`rate`,`freq`,`resovle_freq` from alarm_rule where name=%s'
    res_list = MysqlOp().mysql_dict_query(get_res_sql, [name])
    alarm_dict ={}
    if res_list:
        alarm_dict = res_list[0]
    return alarm_dict



# 加锁
def acquire_lock(lock_name, acquire_timeout=1800, lock_timeout=1800):
    """
    param lock_name: 锁名称
    param acquire_timeout: 客户端获取锁的超时时间
    param lock_timeout: 锁过期时间, 超过这个时间锁自动释放
    """
    redis_cli = RedisClient('dbalarm',decode_responses=True).client
    identifier = str(uuid.uuid4())
    end_time = time.time() + acquire_timeout   # 客户端获取锁的结束时间
    while time.time() <= end_time:
        # setnx(key, value) 只有 key 不存在情况下将 key 设置为 value 返回 True
        # 若 key 存在则不做任何动作,返回 False
        if redis_cli.setnx(lock_name, identifier):
            redis_cli.expire(lock_name, lock_timeout)   # 设置锁的过期时间，防止线程获取锁后崩溃导致死锁
            return identifier   # 返回锁唯一标识
        elif redis_cli.ttl(lock_name) == -1:   # 当锁未被设置过期时间时，重新设置其过期时间
            redis_cli.expire(lock_name, lock_timeout)
        time.sleep(0.001)
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
