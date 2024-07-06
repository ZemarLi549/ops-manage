vim  /etc/sysctl.conf
#添加以下行到文件末尾
vm.max_map_count=262144
sudo sysctl -p