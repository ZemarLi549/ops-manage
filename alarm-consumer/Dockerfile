FROM centos8-python:latest

WORKDIR /alarm-consumer
COPY ./ ./
RUN pip3 install --no-cache-dir -r requirements.txt\
     -i https://mirrors.aliyun.com/pypi/simple/ \
     --trusted-host mirrors.aliyun.com
RUN chmod +x /alarm-consumer/run.sh
ENTRYPOINT ["/bin/bash", "-c","./run.sh"]


