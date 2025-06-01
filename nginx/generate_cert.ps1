# Norsk kommentar: PowerShell script for å generere selvsignert sertifikat for Nginx med OpenSSL

# Opprett certs-mappen hvis den ikke eksisterer
New-Item -ItemType Directory -Force -Path "./certs"

# Generer selvsignert sertifikat med OpenSSL
$opensslCommand = 'openssl req -x509 -nodes -days 365 -newkey rsa:2048 ' + `
                 '-keyout ./certs/privkey.pem ' + `
                 '-out ./certs/cert.pem ' + `
                 '-subj "/C=NO/ST=Oslo/L=Oslo/O=NotatWeb/OU=IT/CN=localhost"'

# Kjør OpenSSL-kommandoen
Write-Host "Genererer selvsignert sertifikat..."
Invoke-Expression $opensslCommand

Write-Host "`nSelvsignert sertifikat er generert i ./certs-mappen"
Write-Host "  - Sertifikat: ./certs/cert.pem"
Write-Host "  - Privat nøkkel: ./certs/privkey.pem"
