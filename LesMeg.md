\***\*##--RUKSANVISNING--##\*\***

Pakk ut zip-fila.
Start PowerShell, stå i mappen som docker-compose.yml ligger.
`docker-compose up -d` ( starter containerne i "detached" modus, kjører i bakgrunnen. Bygges på nytt dersom ikke eksisterer fra før)
eller
`docker-compose up --build` (bygger alltid imagene på nytt)

Logger på med https://localhost/notatweb

For å administrere:
U: admin
P: admin123

Etterpå:
`docker-compose down` (stopper og fjerner alle containere, nettverk, og tilknyttede ressurser)

**Sikkerhet**

Sikker Autentisering og Autorisasjon:

Passord-håndtering:
Passord blir aldri lagret i klartekst, men blir kryptert med Werkzeug's generate_password_hash() før lagring
Passordvalidering gjøres sikkert med check_password_hash() for å sammenligne hasher

JWT (JSON Web Tokens):
Bruker Flask-JWT-Extended for sikker token-basert autentisering
Tokens har en begrenset levetid (1 time) for å redusere risiko ved token-tyveri
Separate hemmelige nøkler for app (SECRET_KEY) og JWT (JWT_SECRET_KEY)

Database Sikkerhet:
Parameteriserte spørringer via SQLAlchemy som beskytter mot SQL-injeksjonsangrep
Databasetilgang er beskyttet med brukernavn og passord
Bruker separate miljøvariabler for databasetilkobling
Cascade delete for å hindre foreldreløse data

HTTPS/SSL Sikkerhet:
Nginx er konfigurert med SSL/TLS:
Tvungen HTTPS-redirect (HTTP til HTTPS)
Støtter kun moderne TLS-protokoller (TLSv1.2 og TLSv1.3)
Bruker sikre cipher suites (HIGH:!aNULL:!MD5)
SSL-sertifikater montert sikkert i containeren

API Sikkerhet:
JWT-beskyttede endepunkter (@jwt_required())
Brukervalidering på alle beskyttede endepunkter

Tilgangskontroll: Brukere kan kun aksessere egne notater
Feilhåndtering og logging for å oppdage og spore sikkerhetshendelser

Infrastruktur Sikkerhet:
Docker-containere kjører isolert i separate nettverk
Volum-montering med read-only tilgang der det er mulig
Miljøvariabler brukes for sensitive data
Helsesjekk på databasen før API starter

CORS (Cross-Origin Resource Sharing):
Konfigurert CORS-policy for API-endepunkter
Kontrollerte HTTP-metoder og headers
Pre-flight requests (OPTIONS) håndteres korrekt

Logging og Overvåkning:
Omfattende logging av feil og sikkerhetshendelser
Nginx access og error logging
API-logging for debugging og feilsøking

Containerisering:
Applikasjonen kjører i isolerte Docker-containere
Separate containere for frontend, backend, database og proxy
Restart-policy for høy tilgjengelighet
Nettverksisolasjon mellom tjenester

**Backups / images**

Dette er mitt depo på Docker Hub:
https://hub.docker.com/repository/docker/donrunar/notatweb/general
donrunar/notatweb

Dette er mitt depo på GitHub:

https://github.com/runarkarlsen/notatweb.git

ṜUͶAЯ KΔR|ƧΞǸ :-)
