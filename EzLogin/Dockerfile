FROM php:7.3-apache

RUN a2enmod rewrite

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt update && \
    apt install -y sqlite3 openssl

COPY src /var/www/html

RUN chown -R www-data:www-data /var/www/html

COPY ./data/db.sql /app/db.sql

COPY ./service/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

WORKDIR /var/www/html

ENTRYPOINT [ "/docker-entrypoint.sh" ]
