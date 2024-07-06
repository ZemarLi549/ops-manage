import redis
class RedisClient(object):
    def __init__(self, dbtype):
        self.host = '172.30.14.39'
        self.port =6379
        self.password = '123456'
        if dbtype == 'dblog':
            self.db = 2
        elif dbtype == 'dbproject':
            self.db = 3
        elif dbtype == 'dbmonitor':
            self.db = 4
        elif dbtype == 'dbalarm':
            self.db = 5
        self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, password=self.password,socket_connect_timeout=1)

    @property
    def client(self):
        return redis.Redis(connection_pool=self.pool)

r = RedisClient('dbmonitor').client
del_keys = r.keys('getsource_comp*')
print(del_keys)
for item in del_keys:
    print(r.get(item))
# if del_keys:
#     r.delete(*del_keys)