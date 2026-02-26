FROM httpd:2.4.49

COPY httpd.conf /usr/local/apache2/conf/httpd.conf

RUN mkdir -p /usr/local/apache2/cgi-bin && \
    echo '#!/bin/sh\necho "Content-type: text/plain\n"\necho "CGI is working"' > /usr/local/apache2/cgi-bin/test.sh && \
    chmod +x /usr/local/apache2/cgi-bin/test.sh

RUN echo "VULNERABLE_CONFIG_DATA_12345" > /usr/local/apache2/htdocs/secret.txt

EXPOSE 80
