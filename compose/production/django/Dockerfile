##############################################
## 基于centos7构建python3运行环境
## 构建命令: 在Dockerfile文件目录下执行 docker build -t centos7-python:3.6 .
## 容器启动命令: docker run -itd --name python --restart always --privileged=true -v /root/dockers/python:/root/python -v /root/dockers/python/cron:/var/spool/cron python-centos:3.5 /usr/sbin/init
## 进入容器：docker exec -it python /bin/bash
###############################################

FROM centos:7.6.1810
MAINTAINER chenmiaomiao # 指定作者信息

#添加文件到镜像
ADD Python-3.6.8.tgz /root/





#安装
RUN set -ex \
    # 预安装所需组件
    && yum install -y wget tar libffi-devel zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make initscripts \
    && cd /root/Python-3.6.8 \
    && ./configure prefix=/usr/local/python3 \
    && make \
    && make install \
    && make clean \
    && rm -rf /root/Python-3.6.8* \
    && yum install -y epel-release --nogpgcheck \
    && yum install -y python-pip

# 设置默认为python3
RUN set -ex \
    # 备份旧版本python
    && mv /usr/bin/python /usr/bin/python27 \
    && mv /usr/bin/pip /usr/bin/pip-python27 \
    # 配置默认为python3
    && ln -s /usr/local/python3/bin/python3.6 /usr/bin/python \
    && ln -s /usr/local/python3/bin/pip3 /usr/bin/pip

# 修复因修改python版本导致yum失效问题
RUN set -ex \
    && sed -i "s#/usr/bin/python#/usr/bin/python27#" /usr/bin/yum \
    && sed -i "s#/usr/bin/python#/usr/bin/python27#" /usr/libexec/urlgrabber-ext-down \
    && yum install -y deltarpm

# 基础环境配置
RUN set -ex \
    # 修改系统时区为东八区
    && rm -rf /etc/localtime \
    && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && yum install -y vim \
    # 安装定时任务组件
    && yum -y install cronie

# 支持中文
RUN yum install kde-l10n-Chinese -y
RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
# 更新pip版本
RUN pip install --upgrade pip
ENV LC_ALL zh_CN.UTF-8


WORKDIR /app/OnlineSchool
COPY requirements.txt .
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
RUN cp /usr/local/python3/bin/gunicorn /usr/local/bin/

COPY . /app/OnlineSchool

COPY cp_to_docker/operations.py /usr/local/python3/lib/python3.6/site-packages/django/db/backends/mysql/operations.py
COPY compose/production/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh




