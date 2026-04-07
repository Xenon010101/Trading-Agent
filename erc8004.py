from web3 import Web3
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

AGENT_REGISTRY = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
HACKATHON_VAULT = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
RISK_ROUTER = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
REPUTATION_REGISTRY = "0x423a9904e39537a9997fbaF0f220d79D7d545763"
VALIDATION_REGISTRY = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"
SEPOLIA_RPC = "https://rpc.sepolia.org"

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


def post_checkpoint(action, symbol, confidence, reason):
    """Record a trading checkpoint"""
    checkpoint = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "symbol": symbol,
        "confidence": confidence,
        "reason": reason,
        "agent": os.getenv("AGENT_ADDRESS", "unknown")
    }
    
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
    create_agent_wallet()
    print("ERC-8004 module ready")
