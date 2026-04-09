import os, time, json
from web3 import Web3
from eth_utils import keccak
from dotenv import load_dotenv

load_dotenv()

RPC = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC))

AGENT_REGISTRY = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
HACKATHON_VAULT = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
RISK_ROUTER = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
VALIDATION_REGISTRY = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"

OPERATOR_PRIVATE_KEY = os.getenv("OPERATOR_PRIVATE_KEY") or os.getenv("AGENT_PRIVATE_KEY")
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
OPERATOR_WALLET = os.getenv("OPERATOR_ADDRESS") or os.getenv("AGENT_ADDRESS")
AGENT_WALLET = os.getenv("AGENT_ADDRESS")
AGENT_ID = int(os.getenv("AGENT_ID", "33"))

# Track nonces to prevent conflicts
_operator_nonce = None
_last_action = None
_last_symbol = None
_checkpoint_counter = 0

RISK_ROUTER_ABI = [
    {
        "name": "submitTradeIntent",
        "type": "function",
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
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "simulateIntent",
        "type": "function",
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
            }
        ],
        "outputs": [
            {"name": "valid", "type": "bool"},
            {"name": "reason", "type": "string"}
        ],
        "stateMutability": "view"
    },
    {
        "name": "getIntentNonce",
        "type": "function",
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view"
    }
]

VALIDATION_ABI = [
    {
        "name": "postEIP712Attestation",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "uint256"},
            {"name": "checkpointHash", "type": "bytes32"},
            {"name": "score", "type": "uint8"},
            {"name": "notes", "type": "string"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "getAverageValidationScore",
        "type": "function",
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view"
    }
]

def submit_trade_intent(action, symbol):
    global _last_action, _last_symbol
    
    print(f"  [DEBUG] Sending intent: {action} {symbol} (Agent ID: {AGENT_ID})")
    
    # Prevent duplicate submissions
    if _last_action == action and _last_symbol == symbol:
        print(f"  [SKIP] Duplicate intent: {action} {symbol}")
        return None
    
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        
        # Check balance before sending
        balance = w3.eth.get_balance(wallet_address)
        required = w3.to_wei(0.003, "ether")
        if balance < required:
            print(f"  [WARN] Low balance ({w3.from_wei(balance, 'ether'):.4f} ETH) - skipping transaction")
            return None
        
        router = w3.eth.contract(
            address=Web3.to_checksum_address(RISK_ROUTER),
            abi=RISK_ROUTER_ABI
        )
        
        # Get nonce from RiskRouter contract (only once)
        nonce = router.functions.getIntentNonce(AGENT_ID).call()
        deadline = int(time.time()) + 300
        
        intent = (
            AGENT_ID,
            wallet_address,
            f"{symbol}USD",
            action,
            50000,
            100,
            nonce,
            deadline
        )
        
        domain_data = {
            "name": "RiskRouter",
            "version": "1",
            "chainId": 11155111,
            "verifyingContract": Web3.to_checksum_address(RISK_ROUTER)
        }
        
        message_types = {
            "TradeIntent": [
                {"name": "agentId", "type": "uint256"},
                {"name": "agentWallet", "type": "address"},
                {"name": "pair", "type": "string"},
                {"name": "action", "type": "string"},
                {"name": "amountUsdScaled", "type": "uint256"},
                {"name": "maxSlippageBps", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint256"},
            ]
        }
        
        message_data = {
            "agentId": AGENT_ID,
            "agentWallet": wallet_address,
            "pair": f"{symbol}USD",
            "action": action,
            "amountUsdScaled": 50000,
            "maxSlippageBps": 100,
            "nonce": nonce,
            "deadline": deadline
        }
        
        signed = w3.eth.account.sign_typed_data(
            private_key=AGENT_PRIVATE_KEY,
            domain_data=domain_data,
            message_types=message_types,
            message_data=message_data
        )
        
        # Simulate first
        valid, reason = router.functions.simulateIntent(intent).call()
        if not valid:
            print(f"  [SKIP] Intent rejected by RiskRouter: {reason}")
            return None
        
        # Get nonce ONCE
        tx_nonce = w3.eth.get_transaction_count(wallet_address, "pending")
        
        # Submit transaction with reduced gas
        tx = router.functions.submitTradeIntent(
            intent,
            signed.signature
        ).build_transaction({
            "from": wallet_address,
            "nonce": tx_nonce,
            "gas": 150000,
            "gasPrice": w3.eth.gas_price,
        })
        
        signed_tx = w3.eth.account.sign_transaction(
            tx, private_key=OPERATOR_PRIVATE_KEY
        )
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  [DEBUG] Tx sent: {tx_hash.hex()}")
        
        # Track for duplicate prevention
        _last_action = action
        _last_symbol = symbol
        
        # Wait for receipt
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            print(f"  ON-CHAIN trade submitted: {action} {symbol}")
            print(f"  TX: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception:
            print(f"  [WARN] Tx pending - will not retry to avoid nonce conflict")
            return tx_hash.hex()
        
    except Exception as e:
        print(f"  [ERR] Trade intent failed: {e}")
        return None

def post_checkpoint(action, symbol, confidence, reason):
    global _operator_nonce
    
    score = int(confidence)
    
    if score == 0:
        print("  [SKIP] Zero confidence checkpoint")
        return
    
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "action": action,
        "confidence": confidence,
        "reason": reason,
        "on_chain": False,
        "score": score
    }
    
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        
        balance = w3.eth.get_balance(wallet_address)
        if balance < w3.to_wei(0.001, "ether"):
            print(f"  [WARN] Low balance ({w3.from_wei(balance, 'ether'):.4f} ETH) - checkpoint saved locally only")
            with open("checkpoints.jsonl", "a") as f:
                f.write(json.dumps(entry) + "\n")
            return
        
        validation = w3.eth.contract(
            address=Web3.to_checksum_address(VALIDATION_REGISTRY),
            abi=VALIDATION_ABI
        )
        
        # Read current score before posting
        try:
            score_before = validation.functions.getAverageValidationScore(AGENT_ID).call()
            print(f"  Score before checkpoint: {score_before}")
        except Exception:
            score_before = None
        
        # Get fresh nonce
        _operator_nonce = w3.eth.get_transaction_count(wallet_address, "pending")
        
        # Create checkpoint hash
        checkpoint_data = {
            "agentId": AGENT_ID,
            "timestamp": int(time.time()),
            "action": action,
            "symbol": symbol,
            "confidence": score
        }
        checkpoint_str = json.dumps(checkpoint_data, sort_keys=True)
        checkpoint_hash = keccak(text=checkpoint_str)
        
        short_notes = reason[:100] if reason else "AI decision"
        
        # Build transaction with optimized gas
        tx = validation.functions.postEIP712Attestation(
            AGENT_ID,
            checkpoint_hash,
            score,
            short_notes
        ).build_transaction({
            "from": wallet_address,
            "nonce": _operator_nonce,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  Checkpoint sent: {action} {symbol} score={score} tx={tx_hash.hex()[:10]}...")
        
        # Wait for receipt and confirmation
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            if receipt.status == 1:
                print(f"  Checkpoint CONFIRMED on-chain")
                entry["tx"] = tx_hash.hex()
                entry["on_chain"] = True
            else:
                print(f"  Checkpoint transaction FAILED (reverted)")
                _operator_nonce = None
        except Exception as e:
            print(f"  Checkpoint receipt timeout - may be pending")
        
        # Verify score updated
        try:
            score_after = validation.functions.getAverageValidationScore(AGENT_ID).call()
            print(f"  Current validation score: {score_after}")
            entry["score_after"] = score_after
        except Exception as e:
            print(f"  Could not verify score: {e}")
        
    except Exception as e:
        print(f"  Checkpoint error: {e}")
        _operator_nonce = None
    
    # Save locally
    with open("checkpoints.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


def test_checkpoint():
    """Test posting one checkpoint and verify the score updates"""
    print("\n" + "=" * 50)
    print("  TESTING CHECKPOINT POSTING")
    print("=" * 50)
    
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        
        validation = w3.eth.contract(
            address=Web3.to_checksum_address(VALIDATION_REGISTRY),
            abi=VALIDATION_ABI
        )
        
        # Read score before
        score_before = validation.functions.getAverageValidationScore(AGENT_ID).call()
        print(f"  Score before: {score_before}")
        
        # Create checkpoint
        checkpoint_data = {
            "agentId": AGENT_ID,
            "timestamp": int(time.time()),
            "action": "TEST",
            "symbol": "BTC",
            "confidence": 75
        }
        checkpoint_str = json.dumps(checkpoint_data, sort_keys=True)
        checkpoint_hash = keccak(text=checkpoint_str)
        
        # Get nonce
        nonce = w3.eth.get_transaction_count(wallet_address, "pending")
        score = 75
        
        tx = validation.functions.postEIP712Attestation(
            AGENT_ID,
            checkpoint_hash,
            score,
            "Test checkpoint from agent"
        ).build_transaction({
            "from": wallet_address,
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  Test checkpoint sent: tx={tx_hash.hex()[:16]}...")
        
        # Wait for confirmation
        print(f"  Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        if receipt.status == 1:
            print(f"  Test checkpoint CONFIRMED")
            
            # Read score after
            score_after = validation.functions.getAverageValidationScore(AGENT_ID).call()
            print(f"  Score after: {score_after}")
            
            if score_after > score_before:
                print(f"  SUCCESS: Score updated from {score_before} to {score_after}")
            else:
                print(f"  WARNING: Score unchanged ({score_before} -> {score_after})")
        else:
            print(f"  FAILED: Transaction reverted on-chain")
            print(f"  Check gas price and balance")
            
    except Exception as e:
        print(f"  TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50 + "\n")


def setup_agent():
    print(f"  ERC-8004 Checkpoints : ACTIVE (ID: {AGENT_ID})")
    test_checkpoint()
