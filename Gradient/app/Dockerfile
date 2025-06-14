FROM php:7.3-apache

RUN a2enmod rewrite

COPY src /var/www/html

RUN chown -R www-data:www-data /var/www/html

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

WORKDIR /var/www/html

ENTRYPOINT [ "/docker-entrypoint.sh" ]
