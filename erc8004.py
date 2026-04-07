from web3 import Web3
import json
import os
import time
import hashlib
from dotenv import load_dotenv

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID", "")

AGENT_REGISTRY = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
HACKATHON_VAULT = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
RISK_ROUTER = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
REPUTATION_REGISTRY = "0x423a9904e39537a9997fbaF0f220d79D7d545763"
VALIDATION_REGISTRY = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"
SEPOLIA_RPC = "https://ethereum-sepolia-rpc.publicnode.com"

# ABIs
AGENT_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "agentWallet", "type": "address"},
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "capabilities", "type": "string[]"},
            {"name": "agentURI", "type": "string"}
        ],
        "name": "register",
        "outputs": [{"name": "agentId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "isRegistered",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getAgent",
        "outputs": [{
            "components": [
                {"name": "operatorWallet", "type": "address"},
                {"name": "agentWallet", "type": "address"},
                {"name": "name", "type": "string"},
                {"name": "description", "type": "string"},
                {"name": "capabilities", "type": "string[]"},
                {"name": "registeredAt", "type": "uint256"},
                {"name": "active", "type": "bool"}
            ],
            "type": "tuple"
        }],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalAgents",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

HACKATHON_VAULT_ABI = [
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "claimAllocation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getBalance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "hasClaimed",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

RISK_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "agentId", "type": "uint256"},
                    {"name": "agentWallet", "type": "address"},
                    {"name": "pair", "type": "string"},
                    {"name": "action", "type": "string"},
                    {"name": "amountUsdScaled", "type": "uint256"},
                    {"name": "maxSlippageBps", "type": "uint256"},
                    {"name": "nonce", "type": "uint256"},
                    {"name": "deadline", "type": "uint256"}
                ],
                "name": "intent",
                "type": "tuple"
            },
            {"name": "signature", "type": "bytes"}
        ],
        "name": "submitTradeIntent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getIntentNonce",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

VALIDATION_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "agentId", "type": "uint256"},
            {"name": "checkpointHash", "type": "bytes32"},
            {"name": "score", "type": "uint8"},
            {"name": "notes", "type": "string"}
        ],
        "name": "postEIP712Attestation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getAverageValidationScore",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))


def create_agent_wallet():
    """Create or load an Ethereum wallet for this agent"""
    existing_key = os.getenv("AGENT_PRIVATE_KEY", "")
    
    if existing_key:
        print(f"Agent wallet already exists: {existing_key[:20]}...")
        account = w3.eth.account.from_key(existing_key)
        return account
    
    account = w3.eth.account.create()
    private_key = account.key.hex()
    address = account.address
    
    env_lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "AGENT_PRIVATE_KEY=" not in line and "AGENT_ADDRESS=" not in line:
                    env_lines.append(line.strip())
    
    env_lines.append(f"AGENT_PRIVATE_KEY={private_key}")
    env_lines.append(f"AGENT_ADDRESS={address}")
    
    with open(".env", "w") as f:
        f.write("\n".join(env_lines) + "\n")
    
    print(f"\n{'='*50}")
    print("  Agent Wallet Created")
    print(f"{'='*50}")
    print(f"  Address: {address}")
    print(f"  Private Key: {private_key[:20]}...")
    print(f"{'='*50}\n")
    
    return account


def save_to_env(key, value):
    """Save a key-value pair to .env"""
    env_lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if f"{key}=" not in line:
                    env_lines.append(line.strip())
    
    env_lines.append(f"{key}={value}")
    
    with open(".env", "w") as f:
        f.write("\n".join(env_lines) + "\n")


def register_agent():
    """Register this agent on the AgentRegistry contract"""
    operator_key = os.getenv("OPERATOR_PRIVATE_KEY", "")
    agent_address = os.getenv("AGENT_ADDRESS", "")
    
    if not operator_key:
        print("[ERR] OPERATOR_PRIVATE_KEY not set in .env")
        print("   Add: OPERATOR_PRIVATE_KEY=your_operator_private_key")
        return None
    
    if not agent_address:
        print("[ERR] AGENT_ADDRESS not set. Run create_agent_wallet() first.")
        return None
    
    if not w3.is_connected():
        print(f"[ERR] Cannot connect to Sepolia RPC: {SEPOLIA_RPC}")
        return None
    
    print(f"\n{'='*50}")
    print("  Registering Agent on Blockchain")
    print(f"{'='*50}")
    
    try:
        registry = w3.eth.contract(address=AGENT_REGISTRY, abi=AGENT_REGISTRY_ABI)
        operator_address = w3.eth.account.from_key(operator_key).address
        
        print(f"  Operator: {operator_address}")
        print(f"  Agent Wallet: {agent_address}")
        
        # Check if agent wallet is already registered
        print("  Checking if agent wallet is already registered...")
        for i in range(1, 41):
            try:
                agent_data = registry.functions.getAgent(i).call()
                if agent_data[1].lower() == agent_address.lower():
                    print(f"  Found! Agent ID: {i}")
                    # Save to .env
                    global AGENT_ID
                    AGENT_ID = str(i)
                    save_to_env("AGENT_ID", str(i))
                    # Call claim_allocation
                    print("  Calling claim_allocation...")
                    claim_allocation()
                    return i
            except:
                continue
        
        print("  Agent wallet not found - proceeding with registration")
        
        # Check operator balance
        balance = w3.eth.get_balance(operator_address)
        print(f"  Operator balance: {w3.from_wei(balance, 'ether')} ETH")
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(operator_address)
        gas_price = w3.eth.gas_price
        
        # Build the transaction
        tx = registry.functions.register(
            agent_address,
            "InsiderEdge",
            "AI trading agent",
            ["trading", "eip712-signing", "risk-management"],
            "https://github.com/your-repo/agent.json"
        ).build_transaction({
            "from": operator_address,
            "nonce": nonce,
            "chainId": 11155111
        })
        
        # Estimate gas
        print("  Estimating gas...")
        try:
            gas = w3.eth.estimate_gas(tx)
            print(f"  Gas estimate: {gas}")
        except Exception as e:
            print(f"  Gas estimation failed (revert reason): {e}")
            return None
        
        # Add explicit gas
        tx["gasPrice"] = gas_price
        tx["gas"] = 500000
        
        # Sign with operator private key
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=operator_key)
        print("  Signing transaction...")
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  TX Hash: {tx_hash.hex()}")
        print("  Waiting for confirmation...")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt["status"] == 1:
            # Extract agentId from logs
            agent_id = None
            for log in receipt["logs"]:
                if log["address"].lower() == AGENT_REGISTRY.lower():
                    if len(log["topics"]) > 1:
                        agent_id = int(log["topics"][1], 16)
                        break
            
            if agent_id is None:
                agent_id = registry.functions.totalAgents().call() - 1
            
            print(f"\n  [OK] Registration Successful!")
            print(f"  Registered agentId: {agent_id}")
            
            save_to_env("AGENT_ID", str(agent_id))
            print(f"  Saved AGENT_ID={agent_id} to .env")
            
            return agent_id
        else:
            print("[ERR] Registration failed - transaction reverted")
            return None
            
    except Exception as e:
        print(f"[ERR] Registration error: {e}")
        return None


def claim_allocation():
    """Claim 0.05 ETH from HackathonVault"""
    operator_key = os.getenv("OPERATOR_PRIVATE_KEY", "")
    agent_id = os.getenv("AGENT_ID", "33")
    
    if not operator_key:
        print("[ERR] OPERATOR_PRIVATE_KEY not set in .env")
        return None
    
    if not w3.is_connected():
        print("[ERR] Cannot connect to Sepolia RPC")
        return None
    
    print(f"\n{'='*50}")
    print("  Claiming Allocation from Vault")
    print(f"{'='*50}")
    
    try:
        vault = w3.eth.contract(address=HACKATHON_VAULT, abi=HACKATHON_VAULT_ABI)
        operator_address = w3.eth.account.from_key(operator_key).address
        
        # Check if already claimed
        has_claimed = vault.functions.hasClaimed(int(agent_id)).call()
        if has_claimed:
            balance = vault.functions.getBalance(int(agent_id)).call()
            eth_balance = w3.from_wei(balance, "ether")
            print(f"  Already claimed: {eth_balance} ETH")
            return balance
        
        # Build and send transaction
        print(f"Claiming vault allocation for Agent ID {agent_id}...")
        nonce = w3.eth.get_transaction_count(operator_address)
        gas_price = w3.eth.gas_price
        
        tx = vault.functions.claimAllocation(int(agent_id)).build_transaction({
            "from": operator_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": gas_price,
            "chainId": 11155111
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=operator_key)
        print("  Sending claim transaction...")
        
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  TX Hash: {tx_hash.hex()}")
        print("  Waiting for confirmation...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt["status"] == 1:
            balance = vault.functions.getBalance(int(agent_id)).call()
            eth_balance = w3.from_wei(balance, "ether")
            print(f"  [SUCCESS] Allocated: {eth_balance} ETH")
            return balance
        else:
            print(f"[ERR] Claim failed - transaction reverted")
            return None
            
    except Exception as e:
        print(f"[ERR] Claim error: {e}")
        return None


def run_claim():
    """Standalone function to claim vault allocation"""
    from dotenv import load_dotenv
    load_dotenv()
    
    status = get_network_status()
    if not status["connected"]:
        print(f"[ERR] Cannot connect to Sepolia RPC")
        return
    
    print(f"\nConnected to Sepolia (Block: {status['block']})")
    claim_allocation()


def submit_trade_intent(action, pair="XBTUSD", amount_usd=500):
    """Submit a trade intent to RiskRouter with EIP-712 signature"""
    agent_key = os.getenv("AGENT_PRIVATE_KEY", "")
    agent_address = os.getenv("AGENT_ADDRESS", "")
    agent_id = os.getenv("AGENT_ID", "")
    
    if not agent_key:
        print("[ERR] AGENT_PRIVATE_KEY not set")
        return None
    
    if not agent_id:
        print("[ERR] AGENT_ID not set. Register first.")
        return None
    
    if not w3.is_connected():
        print("[ERR] Cannot connect to Sepolia RPC")
        return None
    
    try:
        router = w3.eth.contract(address=RISK_ROUTER, abi=RISK_ROUTER_ABI)
        
        # Get nonce
        nonce = router.functions.getIntentNonce(int(agent_id)).call()
        deadline = int(time.time()) + 300
        
        # Build TradeIntent as a proper EIP-712 typed data structure
        intent_data = {
            "agentId": int(agent_id),
            "agentWallet": agent_address,
            "pair": pair,
            "action": action,
            "amountUsdScaled": amount_usd * 100,
            "maxSlippageBps": 100,
            "nonce": nonce,
            "deadline": deadline
        }
        
        # EIP-712 domain separator
        domain = {
            "name": "RiskRouter",
            "version": "1",
            "chainId": 11155111,
            "verifyingContract": RISK_ROUTER
        }
        
        # EIP-712 message types (exclude EIP712Domain - library adds it automatically)
        types = {
            "TradeIntent": [
                {"name": "agentId", "type": "uint256"},
                {"name": "agentWallet", "type": "address"},
                {"name": "pair", "type": "string"},
                {"name": "action", "type": "string"},
                {"name": "amountUsdScaled", "type": "uint256"},
                {"name": "maxSlippageBps", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint256"}
            ]
        }
        
        # Sign using eth_account's sign_typed_data
        from eth_account import Account
        
        signed = Account.sign_typed_data(
            private_key=agent_key,
            domain_data=domain,
            message_types=types,
            message_data=intent_data
        )
        
        # Submit to RiskRouter
        tx = router.functions.submitTradeIntent(
            (
                intent_data["agentId"],
                intent_data["agentWallet"],
                intent_data["pair"],
                intent_data["action"],
                intent_data["amountUsdScaled"],
                intent_data["maxSlippageBps"],
                intent_data["nonce"],
                intent_data["deadline"]
            ),
            signed.signature.hex()
        ).build_transaction({
            "from": agent_address,
            "nonce": w3.eth.get_transaction_count(agent_address),
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 11155111
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=agent_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"  Trade intent submitted: {action} {pair} ({amount_usd} USD)")
        print(f"  TX: {tx_hash.hex()}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"[ERR] Trade intent error: {e}")
        import traceback
        traceback.print_exc()
        return None


def post_validation(agent_id, checkpoint_hash, score, notes):
    """Post attestation to ValidationRegistry on-chain"""
    operator_key = os.getenv("OPERATOR_PRIVATE_KEY", "")
    
    if not operator_key:
        print("[ERR] OPERATOR_PRIVATE_KEY not set")
        return None
    
    if not w3.is_connected():
        print("[ERR] Cannot connect to Sepolia RPC")
        return None
    
    try:
        validation = w3.eth.contract(address=VALIDATION_REGISTRY, abi=VALIDATION_REGISTRY_ABI)
        operator_address = w3.eth.account.from_key(operator_key).address
        
        # Ensure checkpoint_hash is proper bytes32 format
        if isinstance(checkpoint_hash, str):
            # If it's a hex string, convert to bytes32
            if checkpoint_hash.startswith("0x"):
                checkpoint_hash = bytes.fromhex(checkpoint_hash[2:])
            else:
                checkpoint_hash = bytes.fromhex(checkpoint_hash)
        
        # Pad or truncate to 32 bytes
        if len(checkpoint_hash) < 32:
            checkpoint_hash = checkpoint_hash + b'\x00' * (32 - len(checkpoint_hash))
        elif len(checkpoint_hash) > 32:
            checkpoint_hash = checkpoint_hash[:32]
        
        tx = validation.functions.postEIP712Attestation(
            int(agent_id),
            checkpoint_hash,
            int(score),
            notes
        ).build_transaction({
            "from": operator_address,
            "nonce": w3.eth.get_transaction_count(operator_address),
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 11155111
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=operator_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"  Checkpoint posted on-chain")
        print(f"  TX: {tx_hash.hex()}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"[ERR] Validation error: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_network_status():
    """Check connection to Sepolia"""
    try:
        connected = w3.is_connected()
        block = w3.eth.block_number if connected else None
        return {"connected": connected, "block": block}
    except Exception as e:
        return {"connected": False, "error": str(e)}


def post_checkpoint(action, symbol, confidence, reason):
    """Record a trading checkpoint locally and optionally on-chain"""
    from config import PAPER_MODE
    
    checkpoint = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "symbol": symbol,
        "confidence": confidence,
        "reason": reason,
        "agent": os.getenv("AGENT_ADDRESS", "unknown"),
        "agent_id": os.getenv("AGENT_ID", "unregistered")
    }
    
    # Save locally
    filename = "checkpoints.json"
    checkpoints = []
    
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                checkpoints = json.load(f)
        except:
            checkpoints = []
    
    checkpoints.append(checkpoint)
    
    with open(filename, "w") as f:
        json.dump(checkpoints, f, indent=2)
    
    print(f"Checkpoint: [{action}] {symbol} @ {confidence}%")
    
    # Post to ValidationRegistry on-chain if registered and not in paper mode
    agent_id = os.getenv("AGENT_ID", "")
    if agent_id and agent_id != "unregistered" and not PAPER_MODE:
        try:
            # Create a deterministic checkpoint hash from checkpoint data
            checkpoint_data = json.dumps(checkpoint, sort_keys=True)
            checkpoint_hash = hashlib.sha256(checkpoint_data.encode()).digest()
            
            post_validation(agent_id, checkpoint_hash, min(int(confidence), 100), reason)
        except Exception as e:
            print(f"  (On-chain posting skipped: {e})")


def get_checkpoint_summary():
    """Get summary of all checkpoints"""
    filename = "checkpoints.json"
    
    if not os.path.exists(filename):
        print("No checkpoints found")
        return
    
    with open(filename, "r") as f:
        checkpoints = json.load(f)
    
    total = len(checkpoints)
    buys = sum(1 for c in checkpoints if c.get("action") == "BUY")
    sells = sum(1 for c in checkpoints if c.get("action") == "SELL")
    holds = sum(1 for c in checkpoints if c.get("action") == "HOLD")
    
    print(f"\n{'='*40}")
    print("  Checkpoint Summary")
    print(f"{'='*40}")
    print(f"  Total: {total}")
    print(f"  BUY:   {buys}")
    print(f"  SELL:  {sells}")
    print(f"  HOLD:  {holds}")
    print(f"{'='*40}\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  ERC-8004 Integration")
    print("="*50 + "\n")
    
    # Check network
    status = get_network_status()
    if status["connected"]:
        print(f"[OK] Connected to Sepolia (Block: {status['block']})")
    else:
        print(f"[ERR] Not connected: {status.get('error', 'Unknown')}")
    
    print(f"\n  Contract: AgentRegistry")
    print(f"  Address: {AGENT_REGISTRY}")
    
    # Check env
    agent_address = os.getenv("AGENT_ADDRESS", "")
    agent_id = os.getenv("AGENT_ID", "")
    operator_key = os.getenv("OPERATOR_PRIVATE_KEY", "")
    
    if agent_address:
        print(f"\n  Agent Wallet: {agent_address}")
    else:
        print("\n  Creating agent wallet...")
        create_agent_wallet()
    
    if agent_id:
        print(f"  Agent ID: {agent_id}")
    elif operator_key:
        print("\n  Ready to register!")
        print("  Run: register_agent()")
    else:
        print("\n  ⚠️ Add OPERATOR_PRIVATE_KEY to .env to register")
    
    print("\n  Run: python agent.py")
    
    print("\n" + "-"*50)
    print("  Claiming allocation...")
    print("-"*50)
    run_claim()
    print()
