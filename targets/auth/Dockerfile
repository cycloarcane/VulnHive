FROM php:7.2-apache

# Install dependencies for Fuel CMS
RUN apt-get update && apt-get install -y unzip wget libpng-dev libjpeg-dev libfreetype6-dev && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ && docker-php-ext-install gd mysqli pdo pdo_mysql

# Download Fuel CMS 1.4.1 (Vulnerable to Pre-Auth RCE)
WORKDIR /var/www/html
RUN wget https://github.com/daylightstudio/FUEL-CMS/archive/refs/tags/1.4.1.zip && unzip 1.4.1.zip && mv FUEL-CMS-1.4.1/* . && rm -rf FUEL-CMS-1.4.1 1.4.1.zip && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
