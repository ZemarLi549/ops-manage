FROM centos8-python:latest

EXPOSE 8000
WORKDIR /ops-manage-back
COPY ./ ./
RUN pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
RUN chmod +x /ops-manage-back/run.sh
CMD ["bash","/ops-manage-back/run.sh"]
