FROM python:3.8.16

RUN set -ex; \
    apt-get update; \
    apt-get install --no-install-recommends -y \
    nginx \
    supervisor \
    vim \
    ; \
    ( apt-get clean && rm -rf /var/lib/apt/lists/* )

ADD files/zoe-chatboat.conf /etc/supervisor/conf.d/zoe-chatboat.conf
ADD files/start /start
RUN chmod ug+x /start
RUN mkdir -p /var/log/gunicorn
RUN chmod 777 /var/log/gunicorn

ARG PYPI_REPO_URL
ARG PYPI_REPO_URL_HOST
ARG API_VERSION

COPY config/ config/

RUN pip install --upgrade --trusted-host $PYPI_REPO_URL_HOST --index-url $PYPI_REPO_URL zoe-chatboat==$API_VERSION
CMD /start
