for port in `seq 7001 7006`; do \
  mkdir -p /etc/redis_cluster/${port}/conf \
  && PORT=${port} envsubst < ./redis-cluster.tmpl > /etc/redis_cluster/${port}/conf/redis.conf \
  && mkdir -p /data/redis_cluster/${port}/data; \
done