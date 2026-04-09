import os, time, json
from web3 import Web3
from eth_utils import keccak
from dotenv import load_dotenv

load_dotenv()

RPCS = [
    "https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
    "https://rpc.sepolia.org",
    "https://ethereum-sepolia.blockpi.network/v1/rpc/public",
    "https://sepolia.gateway.tenderly.co"
]

w3 = None
for rpc in RPCS:
    try:
        w3_test = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 30}))
        if w3_test.is_connected():
            w3 = w3_test
            print(f"  Connected to Sepolia via: {rpc}")
            break
    except:
        continue

if not w3:
    print("  [ERR] All RPCs failed")

AGENT_REGISTRY = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
HACKATHON_VAULT = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
RISK_ROUTER = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
VALIDATION_REGISTRY = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"
REPUTATION_REGISTRY = "0x0000000000000000000000000000000000000000"

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

REPUTATION_ABI = [
    {
        "name": "submitFeedback",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "uint256"},
            {"name": "score", "type": "uint8"},
            {"name": "outcomeRef", "type": "bytes32"},
            {"name": "comment", "type": "string"},
            {"name": "feedbackType", "type": "uint8"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "name": "getAverageScore",
        "type": "function", 
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view"
    }
]


def get_eip1559_gas_params():
    """Get EIP-1559 gas parameters for Sepolia"""
    try:
        latest_block = w3.eth.get_block('latest')
        base_fee = latest_block.get('baseFeePerGas', w3.eth.gas_price)
        max_priority = w3.to_wei(2, 'gwei')
        max_fee = base_fee * 3 + max_priority
        return {
            "maxFeePerGas": int(max_fee),
            "maxPriorityFeePerGas": int(max_priority),
            "type": 2
        }
    except Exception:
        return {"gasPrice": int(w3.eth.gas_price * 1.2), "type": 0}


def submit_trade_intent(action, symbol):
    global _last_action, _last_symbol
    
    print(f"  [DEBUG] Sending intent: {action} {symbol} (Agent ID: {AGENT_ID})")
    
    if _last_action == action and _last_symbol == symbol:
        print(f"  [SKIP] Duplicate intent: {action} {symbol}")
        return None
    
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        
        balance = w3.eth.get_balance(wallet_address)
        required = w3.to_wei(0.003, "ether")
        if balance < required:
            print(f"  [WARN] Low balance ({w3.from_wei(balance, 'ether'):.4f} ETH) - skipping transaction")
            return None
        
        router = w3.eth.contract(
            address=Web3.to_checksum_address(RISK_ROUTER),
            abi=RISK_ROUTER_ABI
        )
        
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
        
        valid, reason = router.functions.simulateIntent(intent).call()
        if not valid:
            print(f"  [SKIP] Intent rejected by RiskRouter: {reason}")
            return None
        
        latest = w3.eth.get_block('latest')
        base_fee = latest['baseFeePerGas']
        max_fee = base_fee * 3
        priority_fee = w3.to_wei(1, 'gwei')
        
        tx_nonce = w3.eth.get_transaction_count(wallet_address, "pending")
        
        tx = router.functions.submitTradeIntent(
            intent,
            signed.signature
        ).build_transaction({
            "from": wallet_address,
            "nonce": tx_nonce,
            "gas": 150000,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
            "type": 2,
            "chainId": 11155111
        })
        
        signed_tx = w3.eth.account.sign_transaction(
            tx, private_key=OPERATOR_PRIVATE_KEY
        )
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  [DEBUG] Tx sent: {tx_hash.hex()}")
        
        _last_action = action
        _last_symbol = symbol
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=3)
        if receipt.status == 1:
            print(f"  ON-CHAIN trade submitted: {action} {symbol}")
            print(f"  TX: {tx_hash.hex()}")
        else:
            print(f"  ON-CHAIN trade FAILED: {action} {symbol}")
        
        return tx_hash.hex()
        
    except Exception as e:
        print(f"  [ERR] Trade intent failed: {e}")
        return None


def post_checkpoint(action, symbol, confidence, reason):
    try:
        validation = w3.eth.contract(
            address=Web3.to_checksum_address(VALIDATION_REGISTRY),
            abi=VALIDATION_ABI
        )
        
        balance = w3.eth.get_balance(
            Web3.to_checksum_address(OPERATOR_WALLET)
        )
        if balance < w3.to_wei(0.005, 'ether'):
            print(f"  [SKIP] Low balance: {w3.from_wei(balance, 'ether')} ETH")
            return
        
        checkpoint_str = f"{AGENT_ID}{symbol}{action}{int(time.time())}"
        checkpoint_hash = w3.keccak(text=checkpoint_str)
        
        score = min(int(confidence), 100)
        notes = str(reason)[:200] if reason else "AI decision"
        
        gas_price = w3.eth.gas_price
        boosted = int(gas_price * 1.5)
        
        nonce = w3.eth.get_transaction_count(
            Web3.to_checksum_address(OPERATOR_WALLET),
            'pending'
        )
        
        tx = validation.functions.postEIP712Attestation(
            int(AGENT_ID),
            checkpoint_hash,
            score,
            notes
        ).build_transaction({
            "from": Web3.to_checksum_address(OPERATOR_WALLET),
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": boosted
        })
        
        signed_tx = w3.eth.account.sign_transaction(
            tx, private_key=OPERATOR_PRIVATE_KEY
        )
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  Checkpoint TX sent: {tx_hash.hex()[:20]}...")
        
        receipt = w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=120, poll_latency=3
        )
        
        if receipt.status == 1:
            new_score = validation.functions.getAverageValidationScore(
                int(AGENT_ID)
            ).call()
            print(f"  CHECKPOINT CONFIRMED! Validation score: {new_score}")
        else:
            print(f"  Checkpoint reverted")
            
        entry = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "action": action,
            "confidence": confidence,
            "tx": tx_hash.hex()
        }
        with open("checkpoints.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
            
    except Exception as e:
        print(f"  [ERR] Checkpoint: {e}")


def post_reputation(score=90, comment="Autonomous AI trading with risk management"):
    try:
        rep = w3.eth.contract(
            address=Web3.to_checksum_address(REPUTATION_REGISTRY),
            abi=REPUTATION_ABI
        )
        
        outcome_ref = w3.keccak(text=f"InsiderEdge-{AGENT_ID}-{int(time.time())}")
        
        gas_price = w3.eth.gas_price
        boosted = int(gas_price * 1.5)
        
        nonce = w3.eth.get_transaction_count(
            Web3.to_checksum_address(OPERATOR_WALLET),
            'pending'
        )
        
        tx = rep.functions.submitFeedback(
            int(AGENT_ID),
            int(score),
            outcome_ref,
            comment,
            1
        ).build_transaction({
            "from": Web3.to_checksum_address(OPERATOR_WALLET),
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": boosted
        })
        
        signed_tx = w3.eth.account.sign_transaction(
            tx, private_key=OPERATOR_PRIVATE_KEY
        )
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=120, poll_latency=3
        )
        
        if receipt.status == 1:
            avg = rep.functions.getAverageScore(int(AGENT_ID)).call()
            print(f"  REPUTATION CONFIRMED! Score: {avg}")
        else:
            print(f"  Reputation tx reverted")
            
    except Exception as e:
        print(f"  [ERR] Reputation: {e}")


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
        
        score_before = validation.functions.getAverageValidationScore(AGENT_ID).call()
        print(f"  Score before: {score_before}")
        
        checkpoint_data = {
            "agentId": AGENT_ID,
            "timestamp": int(time.time()),
            "action": "TEST",
            "symbol": "BTC",
            "confidence": 75
        }
        checkpoint_str = json.dumps(checkpoint_data, sort_keys=True)
        checkpoint_hash = keccak(text=checkpoint_str)
        
        nonce = w3.eth.get_transaction_count(wallet_address, "pending")
        gas_params = get_eip1559_gas_params()
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
            **gas_params
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  Test checkpoint sent: tx={tx_hash.hex()[:16]}...")
        print(f"  Waiting for confirmation (up to 120s)...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            print(f"  Test checkpoint CONFIRMED")
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
        print(f"  Checkpoint test failed: {e}")
        print(f"  Continuing without on-chain checkpoints...")
    
    print("=" * 50 + "\n")


def setup_agent():
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        balance = w3.eth.get_balance(wallet_address)
        eth_balance = w3.from_wei(balance, 'ether')
        print(f"  Operator ETH balance: {eth_balance} ETH")
        if eth_balance < 0.01:
            print(f"  WARNING: LOW BALANCE - get more Sepolia ETH!")
    except Exception as e:
        print(f"  Could not check balance: {e}")
    
    print(f"  ERC-8004 Checkpoints : ACTIVE (ID: {AGENT_ID})")
    test_checkpoint()
