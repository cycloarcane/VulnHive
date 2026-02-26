FROM php:7.4-apache

# Install dependencies
RUN apt-get update && apt-get install -y unzip wget && rm -rf /var/lib/apt/lists/*

# Download CMSimple 5.15 (Vulnerable to Security Misconfiguration / Default Creds)
WORKDIR /var/www/html
RUN wget https://www.cmsimple.org/downloads_cmsimple50/CMSimple_5-15.zip -O cmsimple.zip && unzip cmsimple.zip && mv CMSimple_5-15/* . && rm -rf CMSimple_5-15 cmsimple.zip && chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

EXPOSE 80
