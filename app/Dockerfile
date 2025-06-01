# Base image
FROM python:3.9-slim

# Sett arbeidskatalog
WORKDIR /app

# Kopier requirements.txt først for å utnytte Docker cache
COPY requirements.txt .

# Installer avhengigheter
RUN pip install --no-cache-dir -r requirements.txt

# Kopier resten av applikasjonen
COPY . .

# Eksponer port 5000
EXPOSE 5000

# Add mysql-connector-python for database connection check
RUN pip install mysql-connector-python

# Make entrypoint script executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Start application using entrypoint script
CMD ["./entrypoint.sh"]
