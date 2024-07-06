mkdir -p /data/dockerMysql/master
mkdir -p /data/dockerMysql/slave
sudo tee /data/dockerMysql/master/my.cnf <<-'EOF'
[mysqld]
character-set-server=utf8
skip-host-cache
skip-name-resolve
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
secure-file-priv=/var/lib/mysql-files
user=mysql
pid-file=/var/run/mysqld/mysqld.pid

log-bin=mysql-bin
server-id=200
binlog-ignore-db=mysql
binlog_format=row

[client]
default-character-set=utf8
socket=/var/run/mysqld/mysqld.sock

!includedir /etc/mysql/conf.d/
EOF

sudo tee /data/dockerMysql/slave/my.cnf <<-'EOF'
[mysqld]
character-set-server=utf8
skip-host-cache
skip-name-resolve
datadir=/var/lib/mysql
socket=/var/run/mysqld/mysqld.sock
secure-file-priv=/var/lib/mysql-files
user=mysql
pid-file=/var/run/mysqld/mysqld.pid

log-bin=mysql-slave-01-bin
server-id=201
relay_log=slave-relay-bin
read-only=1

[client]
default-character-set=utf8
socket=/var/run/mysqld/mysqld.sock

!includedir /etc/mysql/conf.d/
EOF



