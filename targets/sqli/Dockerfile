FROM php:7.4-apache

RUN apt-get update && apt-get install -y unzip wget libmariadb-dev && docker-php-ext-install mysqli pdo pdo_mysql

WORKDIR /var/www/html
RUN wget https://github.com/CuppaCMS/CuppaCMS/archive/refs/heads/master.zip -O cuppa.zip && unzip cuppa.zip && mv CuppaCMS-master/* . && rm -rf CuppaCMS-master cuppa.zip && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
