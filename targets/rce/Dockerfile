FROM php:7.4-apache

RUN apt-get update && apt-get install -y unzip wget libmariadb-dev && docker-php-ext-install mysqli pdo pdo_mysql

WORKDIR /var/www/html
RUN wget https://github.com/thedigicraft/Atom.CMS/archive/refs/heads/master.zip -O atom.zip \
    && unzip atom.zip && mv Atom.CMS-master/* . && rm -rf Atom.CMS-master atom.zip \
    && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
