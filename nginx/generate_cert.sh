#!/bin/sh
# Norsk kommentar: Script for å generere selvsignert sertifikat for Nginx med OpenSSL

mkdir -p ./certs

openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \\
  -keyout ./certs/privkey.pem \\
  -out ./certs/cert.pem \\
  -subj "/C=NO/ST=Oslo/L=Oslo/O=NotatWeb/OU=IT/CN=localhost"

echo "Selvsignert sertifikat generert i ./certs"
