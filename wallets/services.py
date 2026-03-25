import requests, os

# This is the URL of your local Docker container
ENGINE_URL = "http://localhost:3005" 

# This will be the Access Token you get from the dashboard tomorrow
ENGINE_ACCESS_TOKEN = os.getenv("THIRDWEB_ACCESS_TOKEN")

def create_thirdweb_wallet(user_id):
    # The endpoint for a self-hosted Engine is different
    url = f"{ENGINE_URL}/backend-wallet/create"
    
    headers = {
        "Authorization": f"Bearer {ENGINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Self-hosted Engine usually uses a 'label' to identify wallets
    data = {
        "label": f"user_{user_id}"
    }

    response = requests.post(url, json=data, headers=headers)
    
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
    
    if response.status_code == 200:
        result = response.json()
        # The engine returns the address inside a 'result' object
        return {
            "address": result["result"]["walletAddress"],
            "id": result["result"].get("id", "none") 
        }
    else:
        raise Exception(f"Failed to create wallet: {response.text}")
    


def get_wallet_balance(wallet_address, chain="sepolia"):
    """
    Fetches the native token balance (e.g., ETH on Sepolia) for a given wallet.
    """
    url = f"{ENGINE_URL}/backend-wallet/{chain}/{wallet_address}/get-balance"
    
    headers = {
        "Authorization": f"Bearer {ENGINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    
    print("BALANCE STATUS:", response.status_code)
    
    if response.status_code == 200:
        result = response.json()
        # Returns a dictionary with balance details (displayValue, symbol, etc.)
        return result["result"] 
    else:
        return {"displayValue": "0.0", "symbol": "", "error": response.text}