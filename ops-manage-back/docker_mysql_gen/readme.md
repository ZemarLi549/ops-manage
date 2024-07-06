

登录主节点
docker exec -it mysql-master sh
mysql -u root -p -hlocalhost -P 3306
CREATE USER 'repl'@'%' IDENTIFIED WITH 'mysql_native_password' BY 'piecelovewudi';  
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%'; 
flush privileges;
SHOW MASTER STATUS;
docker inspece mysql-master|grep IP

登录从节点
docker exec -it mysql-slave sh
stop slave;
reset slave;
change master to master_host='172.17.0.2',master_user='repl',master_password='123456',MASTER_LOG_FILE='mysql-bin.000001',MASTER_LOG_POS=1378;
start slave;
show slave status;

>https://zhuanlan.zhihu.com/p/654671271


