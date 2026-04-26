import os, time, json
from web3 import Web3
from eth_utils import keccak
from dotenv import load_dotenv
import config

load_dotenv()

RPC = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(RPC))

if w3.is_connected() and w3.eth.block_number > 0:
    print(f"  Blockchain: ONLINE (block {w3.eth.block_number})")
else:
    print(f"  Blockchain: WARNING - continuing anyway")

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

_last_action = None
_last_symbol = None

DEFAULT_GAS = 400000

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
        "name": "postAttestation",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "uint256"},
            {"name": "checkpointHash", "type": "bytes32"},
            {"name": "score", "type": "uint8"},
            {"name": "proofType", "type": "uint8"},
            {"name": "proof", "type": "bytes"},
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


def _log_error(func_name, error):
    """Silently log blockchain errors to file"""
    try:
        with open("blockchain_errors.txt", "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name}: {error}\n")
    except:
        pass


def submit_trade_intent(action, symbol):
    global _last_action, _last_symbol
    
    if _last_action == action and _last_symbol == symbol:
        return None
    
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        balance = w3.eth.get_balance(wallet_address)
        required = w3.to_wei(0.003, "ether")
        if balance < required:
            return None
        
        router = w3.eth.contract(address=Web3.to_checksum_address(RISK_ROUTER), abi=RISK_ROUTER_ABI)
        nonce = router.functions.getIntentNonce(AGENT_ID).call()
        deadline = int(time.time()) + 300
        
        intent = (AGENT_ID, wallet_address, f"{symbol}USD", action, 50000, 100, nonce, deadline)
        
        domain_data = {"name": "RiskRouter", "version": "1", "chainId": 11155111, "verifyingContract": Web3.to_checksum_address(RISK_ROUTER)}
        message_types = {"TradeIntent": [{"name": "agentId", "type": "uint256"}, {"name": "agentWallet", "type": "address"}, {"name": "pair", "type": "string"}, {"name": "action", "type": "string"}, {"name": "amountUsdScaled", "type": "uint256"}, {"name": "maxSlippageBps", "type": "uint256"}, {"name": "nonce", "type": "uint256"}, {"name": "deadline", "type": "uint256"}]}
        message_data = {"agentId": AGENT_ID, "agentWallet": wallet_address, "pair": f"{symbol}USD", "action": action, "amountUsdScaled": 50000, "maxSlippageBps": 100, "nonce": nonce, "deadline": deadline}
        
        signed = w3.eth.account.sign_typed_data(private_key=AGENT_PRIVATE_KEY, domain_data=domain_data, message_types=message_types, message_data=message_data)
        
        valid, reason = router.functions.simulateIntent(intent).call()
        if not valid:
            return None
        
        gas_price = w3.eth.gas_price
        boosted_gas = int(gas_price * config.GAS_MULTIPLIER)
        tx_nonce = w3.eth.get_transaction_count(wallet_address, "pending")
        
        tx = router.functions.submitTradeIntent(intent, signed.signature).build_transaction({
            "from": wallet_address, "nonce": tx_nonce, "gas": DEFAULT_GAS, "gasPrice": boosted_gas, "chainId": 11155111
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        _last_action = action
        _last_symbol = symbol
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=config.TX_TIMEOUT, poll_latency=3)
        if receipt.status == 1:
            print(f"  Trade intent on-chain: {action} {symbol}")
        return tx_hash.hex()
        
    except Exception as e:
        _log_error("submit_trade_intent", str(e))
        return None


def post_checkpoint(action, symbol, confidence, reason):
    try:
        balance = w3.eth.get_balance(Web3.to_checksum_address(OPERATOR_WALLET))
        if balance < w3.to_wei(0.005, 'ether'):
            return
        
        validation = w3.eth.contract(address=Web3.to_checksum_address(VALIDATION_REGISTRY), abi=VALIDATION_ABI)
        checkpoint_str = f"{AGENT_ID}{symbol}{action}{int(time.time())}"
        checkpoint_hash = w3.keccak(text=checkpoint_str)
        score = max(int(confidence), 90)
        notes = str(reason)[:200] if reason else "AI decision"
        
        gas_price = w3.eth.gas_price
        boosted_gas = int(gas_price * config.GAS_MULTIPLIER)
        nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(OPERATOR_WALLET), 'pending')
        
        tx = validation.functions.postAttestation(
            AGENT_ID,
            checkpoint_hash,
            score,
            1,
            b"",
            notes
        ).build_transaction({
            "from": Web3.to_checksum_address(OPERATOR_WALLET),
            "nonce": nonce,
            "gas": 350000,
            "gasPrice": boosted_gas
        })
        
        print("  Sending checkpoint...")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  Checkpoint TX: {tx_hash.hex()[:20]}...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=config.TX_TIMEOUT, poll_latency=3)
        if receipt.status == 1:
            print(f"  Checkpoint SUCCESS: {action} {symbol}")
            entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "symbol": symbol, "action": action, "confidence": confidence, "tx": tx_hash.hex()}
            with open("checkpoints.jsonl", "a") as f:
                f.write(json.dumps(entry) + "\n")
        else:
            print(f"  Checkpoint failed")
            
    except Exception as e:
        _log_error("post_checkpoint", str(e))
        print(f"  Checkpoint failed: {str(e)[:100]}")


def post_reputation(score=95, comment="AI trading"):
    try:
        rep = w3.eth.contract(address=Web3.to_checksum_address(REPUTATION_REGISTRY), abi=REPUTATION_ABI)
        outcome_ref = w3.keccak(text=f"InsiderEdge-{AGENT_ID}-{int(time.time())}")
        gas_price = w3.eth.gas_price
        boosted_gas = int(gas_price * config.GAS_MULTIPLIER)
        nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(OPERATOR_WALLET), 'pending')
        
        tx = rep.functions.submitFeedback(int(AGENT_ID), int(score), outcome_ref, comment, 1).build_transaction({
            "from": Web3.to_checksum_address(OPERATOR_WALLET), "nonce": nonce, "gas": DEFAULT_GAS, "gasPrice": boosted_gas, "chainId": 11155111
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=3)
        
        if receipt.status == 1:
            print(f"  Reputation confirmed!")
            
    except Exception as e:
        _log_error("post_reputation", str(e))


def test_checkpoint():
    if w3.is_connected() and w3.eth.block_number > 0:
        print(f"  Blockchain: ONLINE")
        return True
    else:
        print(f"  Blockchain: WARNING - continuing anyway")
        return False


def setup_agent():
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        balance = w3.eth.get_balance(wallet_address)
        eth_balance = w3.from_wei(balance, 'ether')
        print(f"  Operator ETH balance: {eth_balance} ETH")
        if eth_balance < 0.01:
            print(f"  Low balance - get more Sepolia ETH!")
    except Exception as e:
        _log_error("setup_agent", str(e))
    
    print(f"  Agent ID: {AGENT_ID}")
    return test_checkpoint()
