FROM php:7.4-apache

RUN apt-get update && apt-get install -y libzip-dev unzip wget && docker-php-ext-install zip

WORKDIR /var/www/html
RUN wget https://github.com/WonderCMS/wondercms/releases/download/3.4.2/wondercms-342.zip && unzip wondercms-342.zip && rm wondercms-342.zip && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
