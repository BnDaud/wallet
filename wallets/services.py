import os
import secrets
from eth_account import Account
from cryptography.fernet import Fernet
from decimal import Decimal
from web3 import Web3
from django.conf import settings
import time

# The standard minimal ABI for interacting with any ERC-20 token
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]


RPC_URL = os.getenv("RPC_URL")

# Load the master key
encryption_key = os.getenv("ENCRYPTION_KEY")
cipher_suite = Fernet(encryption_key.encode())

def encrypt_key(plain_text_key):
    return cipher_suite.encrypt(plain_text_key.encode()).decode()

def decrypt_key(encrypted_key):
    return cipher_suite.decrypt(encrypted_key.encode()).decode()

def create_local_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    account = Account.from_key(private_key)
    
    return {
        "address": account.address,
        # We encrypt the key BEFORE returning it to be saved
        "private_key": encrypt_key(private_key) 
    }




def get_w3_instance(chain_id):
    chain_config = settings.BLOCKCHAIN_NETWORKS.get(str(chain_id))
    if not chain_config:
        raise ValueError(f"Chain ID {chain_id} not supported.")
    
    return Web3(Web3.HTTPProvider(chain_config["rpc"]))



def send_asset(sender_wallet, to_address, amount, token_address=None):
    """
    Unified Transfer Function for Sepolia
    - If token_address is None: Sends Native ETH
    - If token_address is '0x...': Sends that ERC-20 Token
    """
    try:
        # 1. Setup connection and decrypt key
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        private_key = decrypt_key(sender_wallet.private_key)
        nonce = w3.eth.get_transaction_count(sender_wallet.address)
        
        # 2. Get current Gas Price from the network
        gas_price = w3.eth.gas_price
        priority_fee = w3.to_wei(2, 'gwei')

        if token_address is None:
            # --- NATIVE ETH LOGIC ---
            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': w3.to_wei(amount, 'ether'),
                'gas': 21000,
                'maxFeePerGas': gas_price + priority_fee,
                'maxPriorityFeePerGas': priority_fee,
                'chainId': 11155111,
            }
        else:
            # --- ERC-20 TOKEN LOGIC ---
            # Define the contract using the address and a standard ABI
            contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
            
            # Auto-detect decimals (CORE=18, USDC=6)
            decimals = contract.functions.decimals().call()
            amount_in_units = int(amount * (10 ** decimals))
            
            # Build the contract 'transfer' transaction
            tx = contract.functions.transfer(to_address, amount_in_units).build_transaction({
                'chainId': 11155111,
                'gas': 65000, # Tokens need more gas to execute code
                'nonce': nonce,
                'maxFeePerGas': gas_price + priority_fee,
                'maxPriorityFeePerGas': priority_fee,
            })

        # 3. Sign and Broadcast
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return w3.to_hex(tx_hash)

    except Exception as e:
        print(f"Transfer Error: {e}")
        return None


w3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_live_balance(address):
    """Fetches balance from the blockchain and converts Wei to ETH."""
    try:
        if not w3.is_address(address):
            return 0.0
        
        balance_wei = w3.eth.get_balance(address)
        # Convert from the smallest unit (Wei) to readable ETH
        return float(w3.from_wei(balance_wei, 'ether'))
    except Exception as e:
        print(f"RPC Error: {e}")
        return 0.0
    

def approve_token(wallet, token_address, spender_address, amount):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    private_key = decrypt_key(wallet.private_key)
    
    contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    decimals = contract.functions.decimals().call()
    amount_in_units = int(amount * (10 ** decimals))
    
    tx = contract.functions.approve(spender_address, amount_in_units).build_transaction({
        'chainId': 11155111,
        'gas': 50000,
        'nonce': w3.eth.get_transaction_count(wallet.address),
        'maxFeePerGas': w3.eth.gas_price,
        'maxPriorityFeePerGas': w3.to_wei(2, 'gwei'),
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    return w3.to_hex(tx_hash)





UNISWAP_V2_ROUTER = "0xC532a74256D3Db42D0Bf7a0400fEFDbad7694008" # Uniswap V2 Router on Sepolia

ROUTER_ABI = [
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]

import time
from web3 import Web3

def execute_swap(wallet, from_token, to_token, amount, slippage_percentage=1.0):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    private_key = decrypt_key(wallet.private_key)
    
    from_contract = w3.eth.contract(address=from_token, abi=ERC20_ABI)
    decimals = from_contract.functions.decimals().call()
    amount_in_units = int(amount * (10 ** decimals))
    
    # --- NEW: Calculate Safe Dynamic Gas ---
    latest_block = w3.eth.get_block('latest')
    base_fee = latest_block['baseFeePerGas']
    priority_fee = w3.to_wei(2, 'gwei')
    
    # Multiply base_fee by 2 to ensure transaction goes through even if network spikes
    safe_max_fee = (base_fee * 2) + priority_fee 
    # ---------------------------------------

    # Step 1: Approve the Router
    approve_tx = from_contract.functions.approve(UNISWAP_V2_ROUTER, amount_in_units).build_transaction({
        'chainId': 11155111,
        'gas': 60000,
        'nonce': w3.eth.get_transaction_count(wallet.address),
        'maxFeePerGas': safe_max_fee,           # UPDATED
        'maxPriorityFeePerGas': priority_fee,   # UPDATED
    })
    
    signed_approve = w3.eth.account.sign_transaction(approve_tx, private_key)
    approve_hash = w3.eth.send_raw_transaction(signed_approve.raw_transaction)
    w3.eth.wait_for_transaction_receipt(approve_hash) 
    
    # Step 2: Calculate Slippage
    router_contract = w3.eth.contract(address=UNISWAP_V2_ROUTER, abi=ROUTER_ABI)
    expected_amounts = router_contract.functions.getAmountsOut(amount_in_units, [from_token, to_token]).call()
    expected_out = expected_amounts[1] 
    slippage_factor = (100 - slippage_percentage) / 100
    amount_out_min = int(expected_out * slippage_factor)
    
    # Step 3: Execute the Swap
    swap_tx = router_contract.functions.swapExactTokensForTokens(
        amount_in_units,
        amount_out_min, 
        [from_token, to_token],
        wallet.address,
        int(time.time()) + 600 
    ).build_transaction({
        'chainId': 11155111,
        'gas': 250000,
        'nonce': w3.eth.get_transaction_count(wallet.address),
        'maxFeePerGas': safe_max_fee,           # UPDATED
        'maxPriorityFeePerGas': priority_fee,   # UPDATED
    })
    
    signed_swap = w3.eth.account.sign_transaction(swap_tx, private_key)
    swap_hash = w3.eth.send_raw_transaction(signed_swap.raw_transaction)
    
    return w3.to_hex(swap_hash)