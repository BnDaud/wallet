import requests , os

THIRDWEB_API_KEY = os.getenv("SECRET_KEY_THIRDWEB")

def create_thirdweb_wallet(email):

 
    url = "https://api.thirdweb.com/v1/wallets"
    
    headers = {
        "Authorization": f"Bearer {THIRDWEB_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email
    }

    response = requests.post(url, json=data, headers=headers)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
    if response.status_code == 200:
        result = response.json()
        return {
            "address": result["address"],
            "id": result["id"]
        }
    else:
        raise Exception("Failed to create wallet")