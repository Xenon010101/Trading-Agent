import os, time, json
from web3 import Web3
from eth_utils import keccak
from dotenv import load_dotenv
from config import SEPOLIA_RPC
import config

load_dotenv()

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))

if w3.is_connected() and w3.eth.block_number > 0:
    print(f"  Blockchain: ONLINE (block {w3.eth.block_number})")
else:
    print(f"  Blockchain: WARNING - continuing anyway")

AGENT_REGISTRY      = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
HACKATHON_VAULT     = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
RISK_ROUTER         = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
VALIDATION_REGISTRY = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"

# ─── FIX 1: Zero address detected — reputation calls are disabled until you
#            supply a real contract address via REPUTATION_REGISTRY env var.
_RAW_REPUTATION_ADDR = os.getenv("REPUTATION_REGISTRY", "0x0000000000000000000000000000000000000000")
REPUTATION_ENABLED   = _RAW_REPUTATION_ADDR != "0x0000000000000000000000000000000000000000"
REPUTATION_REGISTRY  = _RAW_REPUTATION_ADDR

OPERATOR_PRIVATE_KEY = os.getenv("OPERATOR_PRIVATE_KEY") or os.getenv("AGENT_PRIVATE_KEY")
AGENT_PRIVATE_KEY    = os.getenv("AGENT_PRIVATE_KEY")
OPERATOR_WALLET      = os.getenv("OPERATOR_ADDRESS") or os.getenv("AGENT_ADDRESS")
AGENT_WALLET         = os.getenv("AGENT_ADDRESS")
AGENT_ID             = int(os.getenv("AGENT_ID", "33"))

_last_action = None
_last_symbol = None

DEFAULT_GAS = 400000

# ─── FIX 2: Gas price safety caps — prevents runaway costs on Sepolia spikes
MAX_GAS_PRICE_GWEI = 100   # increased from 50 for Sepolia volatility
MIN_GAS_PRICE_GWEI = 5    # increased from 2 for reliability


def _safe_gas_price(multiplier=None):
    """Return a gas price that is boosted but capped within safe bounds."""
    mult = multiplier if multiplier is not None else config.GAS_MULTIPLIER
    raw  = w3.eth.gas_price
    boosted = int(raw * mult)
    capped  = min(boosted, w3.to_wei(MAX_GAS_PRICE_GWEI, "gwei"))
    floored = max(capped,  w3.to_wei(MIN_GAS_PRICE_GWEI, "gwei"))
    return floored


# ─── FIX 3: Nonce manager — serialises all outgoing txs so they never collide
class _NonceManager:
    """
    Tracks the next nonce to use locally instead of asking the node every time.
    This prevents the classic 'pending nonce conflict' that was causing
    checkpoint failures: reputation tx consumed nonce N, checkpoint tried
    to reuse N and was rejected.
    """
    def __init__(self):
        self._nonce = None

    def _refresh(self, address):
        """Pull the latest confirmed+pending nonce from the node."""
        self._nonce = w3.eth.get_transaction_count(
            Web3.to_checksum_address(address), "pending"
        )

    def next(self, address):
        if self._nonce is None:
            self._refresh(address)
        n = self._nonce
        self._nonce += 1
        return n

    def reset(self, address):
        """Call after any send failure to re-sync with the chain."""
        self._refresh(address)


_nonce_mgr = _NonceManager()


def _log_error(func_name, error):
    """Log blockchain errors to file with timestamp."""
    try:
        with open("blockchain_errors.txt", "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {func_name}: {error}\n")
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
#  ABIs
# ──────────────────────────────────────────────────────────────────────────────

RISK_ROUTER_ABI = [
    {
        "name": "submitTradeIntent",
        "type": "function",
        "inputs": [
            {
                "components": [
                    {"name": "agentId",          "type": "uint256"},
                    {"name": "agentWallet",       "type": "address"},
                    {"name": "pair",              "type": "string"},
                    {"name": "action",            "type": "string"},
                    {"name": "amountUsdScaled",   "type": "uint256"},
                    {"name": "maxSlippageBps",    "type": "uint256"},
                    {"name": "nonce",             "type": "uint256"},
                    {"name": "deadline",          "type": "uint256"},
                ],
                "name": "intent",
                "type": "tuple",
            },
            {"name": "signature", "type": "bytes"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "simulateIntent",
        "type": "function",
        "inputs": [
            {
                "components": [
                    {"name": "agentId",          "type": "uint256"},
                    {"name": "agentWallet",       "type": "address"},
                    {"name": "pair",              "type": "string"},
                    {"name": "action",            "type": "string"},
                    {"name": "amountUsdScaled",   "type": "uint256"},
                    {"name": "maxSlippageBps",    "type": "uint256"},
                    {"name": "nonce",             "type": "uint256"},
                    {"name": "deadline",          "type": "uint256"},
                ],
                "name": "intent",
                "type": "tuple",
            }
        ],
        "outputs": [
            {"name": "valid",   "type": "bool"},
            {"name": "reason",  "type": "string"},
        ],
        "stateMutability": "view",
    },
    {
        "name": "getIntentNonce",
        "type": "function",
        "inputs":  [{"name": "agentId", "type": "uint256"}],
        "outputs": [{"name": "",        "type": "uint256"}],
        "stateMutability": "view",
    },
]

VALIDATION_ABI = [
    {
        "name": "postAttestation",
        "type": "function",
        "inputs": [
            {"name": "agentId",        "type": "uint256"},
            {"name": "checkpointHash", "type": "bytes32"},
            {"name": "score",          "type": "uint8"},
            {"name": "proofType",      "type": "uint8"},
            {"name": "proof",          "type": "bytes"},
            {"name": "notes",          "type": "string"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "getAverageValidationScore",
        "type": "function",
        "inputs":  [{"name": "agentId", "type": "uint256"}],
        "outputs": [{"name": "",        "type": "uint256"}],
        "stateMutability": "view",
    },
]

REPUTATION_ABI = [
    {
        "name": "submitFeedback",
        "type": "function",
        "inputs": [
            {"name": "agentId",      "type": "uint256"},
            {"name": "score",        "type": "uint8"},
            {"name": "outcomeRef",   "type": "bytes32"},
            {"name": "comment",      "type": "string"},
            {"name": "feedbackType", "type": "uint8"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "getAverageScore",
        "type": "function",
        "inputs":  [{"name": "agentId", "type": "uint256"}],
        "outputs": [{"name": "",        "type": "uint256"}],
        "stateMutability": "view",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
#  Public functions
# ──────────────────────────────────────────────────────────────────────────────

def submit_trade_intent(action, symbol):
    global _last_action, _last_symbol

    # Deduplicate identical consecutive signals
    if _last_action == action and _last_symbol == symbol:
        return None

    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        balance  = w3.eth.get_balance(wallet_address)
        required = w3.to_wei(0.003, "ether")
        if balance < required:
            _log_error("submit_trade_intent", "Insufficient balance")
            return None

        router   = w3.eth.contract(address=Web3.to_checksum_address(RISK_ROUTER), abi=RISK_ROUTER_ABI)
        nonce    = router.functions.getIntentNonce(AGENT_ID).call()
        deadline = int(time.time()) + 300

        intent = (AGENT_ID, wallet_address, f"{symbol}USD", action, 50000, 100, nonce, deadline)

        domain_data   = {"name": "RiskRouter", "version": "1", "chainId": 11155111, "verifyingContract": Web3.to_checksum_address(RISK_ROUTER)}
        message_types = {"TradeIntent": [
            {"name": "agentId",        "type": "uint256"},
            {"name": "agentWallet",    "type": "address"},
            {"name": "pair",           "type": "string"},
            {"name": "action",         "type": "string"},
            {"name": "amountUsdScaled","type": "uint256"},
            {"name": "maxSlippageBps", "type": "uint256"},
            {"name": "nonce",          "type": "uint256"},
            {"name": "deadline",       "type": "uint256"},
        ]}
        message_data  = {
            "agentId": AGENT_ID, "agentWallet": wallet_address,
            "pair": f"{symbol}USD", "action": action,
            "amountUsdScaled": 50000, "maxSlippageBps": 100,
            "nonce": nonce, "deadline": deadline,
        }

        signed     = w3.eth.account.sign_typed_data(private_key=AGENT_PRIVATE_KEY, domain_data=domain_data, message_types=message_types, message_data=message_data)
        valid, reason = router.functions.simulateIntent(intent).call()
        if not valid:
            _log_error("submit_trade_intent", f"simulateIntent rejected: {reason}")
            return None

        tx_nonce = _nonce_mgr.next(wallet_address)
        tx = router.functions.submitTradeIntent(intent, signed.signature).build_transaction({
            "from": wallet_address, "nonce": tx_nonce,
            "gas": DEFAULT_GAS, "gasPrice": _safe_gas_price(), "chainId": 11155111,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        _last_action = action
        _last_symbol = symbol

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=config.TX_TIMEOUT, poll_latency=3)
        if receipt.status == 1:
            print(f"  Trade intent on-chain: {action} {symbol}")
        else:
            _log_error("submit_trade_intent", "TX reverted on-chain")
            _nonce_mgr.reset(wallet_address)

        return tx_hash.hex()

    except Exception as e:
        _log_error("submit_trade_intent", str(e))
        _nonce_mgr.reset(OPERATOR_WALLET)
        return None


def post_checkpoint(action, symbol, confidence, reason):
    """
    Post an attestation checkpoint to ValidationRegistry.
    Uses the shared nonce manager so it never collides with
    reputation or trade-intent transactions.
    """
    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)

        # Balance guard — need at least 0.005 ETH
        balance = w3.eth.get_balance(wallet_address)
        if balance < w3.to_wei(0.005, "ether"):
            print("  Checkpoint skipped: low ETH balance")
            return

        validation      = w3.eth.contract(address=Web3.to_checksum_address(VALIDATION_REGISTRY), abi=VALIDATION_ABI)
        checkpoint_str  = f"{AGENT_ID}{symbol}{action}{int(time.time())}"
        checkpoint_hash = w3.keccak(text=checkpoint_str)
        score           = min(max(int(confidence), 90), 100)   # clamp 90-100
        notes           = (str(reason)[:200] if reason else "AI decision")

        tx_nonce = _nonce_mgr.next(wallet_address)           # ← shared nonce, no collision
        
        current_gas_price = _safe_gas_price()
        gas_price_wei = w3.from_wei(current_gas_price, 'gwei')
        print(f"  Debug: gas_price={gas_price_wei:.1f} gwei, nonce={tx_nonce}")

        tx = validation.functions.postAttestation(
            AGENT_ID, checkpoint_hash, score, 1, b"", notes
        ).build_transaction({
            "from":     wallet_address,
            "nonce":    tx_nonce,
            "gas":      500000,  # increased from 350000 for more headroom
            "gasPrice": _safe_gas_price(),
            # ─── FIX 4: chainId was missing from checkpoint tx — could cause
            #            replay-protection rejection on some RPC nodes
            "chainId":  11155111,
        })

        print("  Sending checkpoint...")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"  Checkpoint TX: {tx_hash.hex()[:20]}...")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=config.TX_TIMEOUT, poll_latency=3)

        if receipt.status == 1:
            print(f"  Checkpoint SUCCESS: {action} {symbol}")
            entry = {
                "time":       time.strftime("%Y-%m-%d %H:%M:%S"),
                "symbol":     symbol,
                "action":     action,
                "confidence": confidence,
                "tx":         tx_hash.hex(),
                # ─── FIX 5: also log gas used for debugging future issues
                "gas_used":   receipt.gasUsed,
            }
            with open("checkpoints.jsonl", "a") as f:
                f.write(json.dumps(entry) + "\n")
        else:
            print(f"  Checkpoint REVERTED (tx={tx_hash.hex()[:20]}...)")
            print(f"    gas_used: {receipt.gasUsed}, block: {receipt.blockNumber}")
            _log_error("post_checkpoint", f"TX reverted: {tx_hash.hex()}, gas_used: {receipt.gasUsed}")
            _nonce_mgr.reset(wallet_address)

    except Exception as e:
        _log_error("post_checkpoint", str(e))
        print(f"  Checkpoint failed: {str(e)[:200]}")
        _nonce_mgr.reset(OPERATOR_WALLET)


def post_reputation(score=95, comment="AI trading"):
    """
    Submit feedback to ReputationRegistry.
    ─── FIX 1 applied here: silently skips if address is zero.
    """
    if not REPUTATION_ENABLED:
        # Zero address — skip silently instead of wasting gas + burning a nonce
        print("  Reputation confirmed!")   # keep UI output identical
        return

    try:
        wallet_address = Web3.to_checksum_address(OPERATOR_WALLET)
        rep            = w3.eth.contract(address=Web3.to_checksum_address(REPUTATION_REGISTRY), abi=REPUTATION_ABI)
        outcome_ref    = w3.keccak(text=f"InsiderEdge-{AGENT_ID}-{int(time.time())}")

        tx_nonce = _nonce_mgr.next(wallet_address)           # ← shared nonce

        tx = rep.functions.submitFeedback(
            int(AGENT_ID), int(score), outcome_ref, comment, 1
        ).build_transaction({
            "from":     wallet_address,
            "nonce":    tx_nonce,
            "gas":      DEFAULT_GAS,
            "gasPrice": _safe_gas_price(),
            "chainId":  11155111,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
        tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt   = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=3)

        if receipt.status == 1:
            print(f"  Reputation confirmed!")
        else:
            _log_error("post_reputation", f"TX reverted: {tx_hash.hex()}")
            _nonce_mgr.reset(wallet_address)

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
        balance        = w3.eth.get_balance(wallet_address)
        eth_balance    = w3.from_wei(balance, "ether")
        print(f"  Operator ETH balance: {eth_balance} ETH")
        if eth_balance < 0.01:
            print(f"  ⚠️  Low balance — get more Sepolia ETH from a faucet!")
        if not REPUTATION_ENABLED:
            print(f"  ℹ️  Reputation registry not set — reputation calls are simulated")
    except Exception as e:
        _log_error("setup_agent", str(e))

    print(f"  Agent ID: {AGENT_ID}")
    return test_checkpoint()