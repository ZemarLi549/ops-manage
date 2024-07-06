#git pull origin master
git pull
docker build -t artifacts.iflytek.com/stc-docker-private/lizengxin/ops-manage-back:v1.3 .
docker rm -f ops-manage-back1
docker rm -f ops-manage-back2
#-v /data/lizengxin/envs/.local:/ops-manage-back/.local


 docker run -itd -v /etc/localtime:/etc/localtime:ro --name=ops-manage-back2 -p 8001:8000  -v /data/.local:/ops-manage-back/.local -v /data/applications/ops_manage:/data/applications/ops_manage --restart=always artifacts.iflytek.com/stc-docker-private/lizengxin/ops-manage-back:v1.3

docker run -itd  -v /etc/localtime:/etc/localtime:ro --name=ops-manage-back1 -p 8000:8000  -v /data/.local:/ops-manage-back/.local -v /data/applications/ops_manage:/data/applications/ops_manage --restart=always artifacts.iflytek.com/stc-docker-private/lizengxin/ops-manage-back:v1.3