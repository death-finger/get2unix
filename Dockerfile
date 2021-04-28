FROM python:3.8-alpine

COPY requirements.txt /tmp/
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add gcc mariadb-connector-c-dev libgsasl-dev openldap-dev openssl-dev libffi-dev musl-dev make libjpeg-turbo-dev && \
    pip install --no-cache-dir -r /tmp/requirements.txt -i http://registry/repository/pypi/simple --trusted-host registry && \
    rm -f /tmp/requirements.txt
WORKDIR /code

