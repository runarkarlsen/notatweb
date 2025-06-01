-- Opprett database
CREATE DATABASE IF NOT EXISTS notatweb;
USE notatweb;

-- Opprett bruker med rettigheter
CREATE USER IF NOT EXISTS 'notatweb_user'@'%' IDENTIFIED BY 'notatweb_password';
GRANT ALL PRIVILEGES ON notatweb.* TO 'notatweb_user'@'%';
FLUSH PRIVILEGES;

-- Opprett tabeller
CREATE TABLE IF NOT EXISTS bruker (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brukernavn VARCHAR(80) UNIQUE NOT NULL,
    passord_hash VARCHAR(120) NOT NULL,
    er_admin BOOLEAN DEFAULT FALSE,  -- Ny kolonne for å markere admin-brukere
    opprettet DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tittel VARCHAR(100) NOT NULL,
    innhold TEXT NOT NULL,
    opprettet DATETIME DEFAULT CURRENT_TIMESTAMP,
    bruker_id INT NOT NULL,
    FOREIGN KEY (bruker_id) REFERENCES bruker(id) ON DELETE CASCADE  -- Legg til CASCADE for automatisk sletting
);

-- Admin-bruker vil bli opprettet automatisk av applikasjonen ved oppstart
-- Dette sikrer at riktig passord-hash blir generert
