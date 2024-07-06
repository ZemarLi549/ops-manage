# ops_management
##mac
conda install -c conda-forge uwsgi


## 启动
```shell
#可编辑环境变量
mkdir -p /data/.local
sudo tee /data/.local/.env <<-'EOF'
DJANGO_SETTINGS_MODULE=ops_manage.settings
MYSQL_DB_HOST=172.30.14.37
MYSQL_DB_PORT=3306
MYSQL_DB_USER=root
MYSQL_DB_PASSWD=123456
MYSQL_DB_NAME=ops_manage
GIT_REPO_URL=xxx
GIT_REPO_PATH=xxx
REDIS_HOST=172.30.14.37
REDIS_PASSWORD=123456
REDIS_PORT=6379
OPS_DOMAIN=http://127.0.0.1:8000
LOGLEVEL=INFO
ES_HOSTS=http://127.0.0.1:9200
ES_USERNAME=elastic
ES_PWD=123456
SSO_VALIDATE=https://sso.com
EOF

启动时挂载  -v /data/.local:/ops-manage-back/.local，即可用环境变量
```
```shell


#启动
docker run -itd --name=ops-manage-back -p 8000:8000  -v /data/applications/ops_manage:/data/applications/ops_manage --restart=always hub.com/ops-manage-back:v1.0
#修改 可访问的mysql数据库账号，redis账号
```
