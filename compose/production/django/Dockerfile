# Install the base requirements for the app.
# This stage is to support development.
FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && apk update \
  # Pillow dependencies
  && apk add --no-cache --virtual .pynacl_deps bash jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev musl-dev libffi-dev openssl-dev python3-dev gcc build-base libressl-dev

RUN apk add tzdata
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime


WORKDIR /app/OnlineSchool

COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple

 COPY . /app/OnlineSchool

COPY cp_to_docker/operations.py /usr/local/lib/python3.6/site-packages/django/db/backends/mysql/operations.py
COPY compose/production/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh