sudo yum -y remove docker \
docker-common \
container-selinux \
docker-selinux \
docker-engine

rm -fr /var/lib/docker/


yum install -y yum-utils.noarch

yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

sudo tee /etc/docker/daemon.json <<-'EOF'
{
    "registry-mirrors": [
        "https://registry.hub.docker.com",
        "http://hub-mirror.c.163.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://registry.docker-cn.com"
    ]
}
EOF

sudo systemctl daemon-reload

#yum list docker-ce --showduplicates | sort -r
yum -y install  docker-ce-24.0.5-1.el7
#docker命令补全工具
yum install -y bash-completion
systemctl start docker
systemctl enable docker

#docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
#docker-compose up -d --force-recreate