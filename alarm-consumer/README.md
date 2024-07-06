# ops_management
##mac
conda install -c conda-forge uwsgi

## 启动
```shell
mkdir -p /data/alarm-consumer/.env
mkdir -p /data/logs
sudo tee /data/alarm-consumer/.env<<-'EOF'
MYSQL_DB_HOST=172.30.14.37
MYSQL_DB_PORT=3306
MYSQL_DB_USER=root
MYSQL_DB_PASSWD=123456
MYSQL_DB_NAME=ops_manage
REDIS_HOST=172.30.14.37
REDIS_PASSWORD=123456
REDIS_PORT=6379
REDIS_DB=10
LOG_LEVEL=INFO
OPSMANAGE_DOMAIN=http://127.0.0.1:8098
SMS_URL=http://xxx/tencloudsms.action
SMS_PASS=xxx-xxx
ES_HOSTS=http://172.30.14.37:9300
ES_USERNAME=elastic
ES_PWD=123456
EOF

启动时挂载  -v /data/alarm-consumer/.env:/alarm-consumer/.env
#启动
docker run -itd --name=alarm-consumer2 -v /etc/localtime:/etc/localtime:ro -v /data/alarm-consumer/.env:/alarm-consumer/.env -v /data/logs/alarm-consumer:/data/logs/alarm-consumer --restart=always hub.com/alarm-consumer:v1.0
#修改 可访问的mysql数据库账号，redis账号
```
## 更新
```shell
#v1.0 最好改动
git pull
docker build -t hub.com/alarm-consumer:v1.0 .
docker rm -f alarm-consumer1
docker run ...
```