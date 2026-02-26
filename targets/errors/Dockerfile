FROM php:7.4-apache

# Set a sensitive environment variable
ENV VULNHIVE_INTERNAL_KEY="HIVE-TOP-SECRET-12345"

# Create a script that crashes and leaks info on bad input (Consolidated to single line)
RUN echo '<?php ini_set("display_errors", 1); error_reporting(E_ALL); if (isset($_GET["crash"])) { throw new Exception("Unexpected state. Internal Key: " . getenv("VULNHIVE_INTERNAL_KEY")); } ?><h1>Exceptional Conditions Node</h1><p>Normal operation active.</p>' > /var/www/html/index.php

EXPOSE 80
