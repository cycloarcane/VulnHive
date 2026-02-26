FROM php:7.4-apache

# Install dependencies
RUN apt-get update && apt-get install -y unzip wget libmariadb-dev && docker-php-ext-install mysqli pdo pdo_mysql

# Download Bus Pass Management System 1.0 (Vulnerable to IDOR & XSS)
WORKDIR /var/www/html
RUN wget https://github.com/shouvikdutta1998/Bus_management/archive/refs/heads/master.zip -O bus.zip && unzip bus.zip && mv Bus_management-main/* . && rm -rf Bus_management-main bus.zip && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
