# Base image
FROM nginx:alpine

# Kopier nginx konfigurasjon
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Kopier web filer
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

# Eksponer port 80
EXPOSE 80

# Nginx kjører automatisk som CMD
