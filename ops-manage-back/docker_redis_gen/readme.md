-- 集群、分配插槽
docker exec -it redis-7001 redis-cli -p 7001 -a pieceloveredis --cluster create 172.30.92.180:7001 172.30.92.180:7002 172.30.92.180:7003 172.30.92.180:7004 172.30.92.180:7005 172.30.92.180:7006 --cluster-replicas 1

-- 测试
docker exec -it redis-7001 redis-cli -h 172.30.92.180 -p 7003 -a pieceloveredis -c
-- 查看集群状态
cluster nodes
-- 查看分片信息
cluster slots
-- 查看集群信息
cluster info


## 添加节点
docker-compose -f add-redis-docker.yml up
-- 进入任意节点
docker exet -it redis-7001 bash

-- 添加主节点(172.30.92.180:7001 -a 123456  这个可以是任何已存在的节点，主要用于获取集群信息)
redis-cli --cluster add-node 172.30.92.180:7007 172.30.92.180:7001 -a 123456
> https://www.php.cn/faq/551060.html
> 
> 
单节点添加 ：docker run -itd --name myRedis -p 7001:6379  --privileged=true  -v /var/redis/data:/data -v /usr/local/redis/redis.conf:/etc/redis/redis.conf --restart=always redis:6 redis-server /etc/redis/redis.conf