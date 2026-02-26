FROM php:7.4-apache

RUN apt-get update && apt-get install -y libpng-dev libjpeg-dev libfreetype6-dev libxml2-dev libicu-dev libzip-dev libc-client-dev libkrb5-dev unzip wget && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-configure gd --with-freetype --with-jpeg && docker-php-ext-configure imap --with-kerberos --with-imap-ssl && docker-php-ext-install -j$(nproc) gd mysqli pdo_mysql xml intl gettext imap zip

WORKDIR /var/www/html
RUN wget https://github.com/osTicket/osTicket/releases/download/v1.14.2/osTicket-v1.14.2.zip && unzip osTicket-v1.14.2.zip && rm osTicket-v1.14.2.zip && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
