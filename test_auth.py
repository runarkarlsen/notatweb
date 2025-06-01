import requests
import json
from urllib3.exceptions import InsecureRequestWarning
# Deaktiver SSL-advarsler for testing med selv-signerte sertifikater
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = "https://localhost/api"

def test_auth():
    """
    Tester autentiseringsfunksjonalitet for NotatWeb API
    Prøver å logge inn som admin og teste debug-endepunktet
    """
    # Admin innloggingsdata
    admin_data = {
        "brukernavn": "admin",
        "passord": "admin123"
    }
    
    # Prøv å logge inn som admin
    print("Tester admin innlogging...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json=admin_data,
            verify=False  # Ignorer SSL-sertifikatvalidering for testing
        )
        print(f"Innlogging respons: {login_response.status_code}")
        print(f"Innlogging innhold: {login_response.text}\n")
        
        if login_response.status_code == 200:
            # Hent JWT-token fra responsen
            token = login_response.json().get('access_token')
            
            # Test feilsøkingsendepunktet med token
            print("Tester feilsøkingsendepunkt med token...")
            headers = {'Authorization': f'Bearer {token}'}
            debug_response = requests.get(
                f"{BASE_URL}/notes/debug",
                headers=headers,
                verify=False
            )
            print(f"Debug respons: {debug_response.status_code}")
            print(f"Debug innhold: {debug_response.text}")
    except Exception as e:
        print(f"Innlogging/Debug feil: {e}")

if __name__ == "__main__":
    test_auth()
