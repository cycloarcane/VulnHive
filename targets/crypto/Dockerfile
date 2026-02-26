FROM php:7.4-apache

# Install dependencies
RUN apt-get update && apt-get install -y unzip wget libmariadb-dev && docker-php-ext-install mysqli pdo pdo_mysql

# Download SweetRice 1.5.1 (Vulnerable to A02: MD5 Hash exposure in backups)
WORKDIR /var/www/html
RUN wget https://www.sweetrice.xyz/attachment/sweetrice-1.5.1.zip -O sweetrice.zip && unzip sweetrice.zip && mv sweetrice/* . && rm -rf sweetrice sweetrice.zip && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
