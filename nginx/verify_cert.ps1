# Norsk kommentar: PowerShell script for å verifisere SSL sertifikat

# Sjekk om sertifikatfilen eksisterer
if (Test-Path "./certs/cert.pem") {
    Write-Host "Verifiserer sertifikat informasjon...`n"
    
    # Vis detaljert informasjon om sertifikatet
    $opensslCommand = 'openssl x509 -in ./certs/cert.pem -text -noout'
    
    Write-Host "Sertifikat detaljer:"
    Write-Host "===================="
    Invoke-Expression $opensslCommand
} else {
    Write-Host "Feil: Sertifikatfilen (cert.pem) ble ikke funnet i ./certs-mappen"
    Write-Host "Vennligst generer sertifikatet først ved å kjøre generate_cert.ps1"
}
