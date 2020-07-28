# Install the base requirements for the app.
# This stage is to support development.
FROM nginx:1.17.1

# 替换为国内源
#RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
#COPY ./compose/production/nginx/sources.list /etc/apt/
RUN apt-get update && apt-get install -y --allow-unauthenticated --assume-yes apt-utils certbot python-certbot-nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY ./compose/production/nginx/OnlineSchool.conf /etc/nginx/conf.d/OnlineSchool.conf
