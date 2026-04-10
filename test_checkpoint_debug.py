from erc8004 import w3, VALIDATION_REGISTRY, OPERATOR_WALLET, OPERATOR_PRIVATE_KEY
from web3 import Web3
import time

VALIDATION_ABI = [
    {'name': 'postEIP712Attestation', 'type': 'function', 'inputs': [{'name': 'agentId', 'type': 'uint256'}, {'name': 'checkpointHash', 'type': 'bytes32'}, {'name': 'score', 'type': 'uint8'}, {'name': 'notes', 'type': 'string'}], 'outputs': [], 'stateMutability': 'nonpayable'}
]

validation = w3.eth.contract(address=Web3.to_checksum_address(VALIDATION_REGISTRY), abi=VALIDATION_ABI)
checkpoint_hash = w3.keccak(text=f'test4-{int(time.time())}')

# Estimate gas first
try:
    gas_estimate = validation.functions.postEIP712Attestation(33, checkpoint_hash, 75, 'test').estimate_gas({'from': Web3.to_checksum_address(OPERATOR_WALLET)})
    print(f'Gas estimate: {gas_estimate}')
    gas_to_use = int(gas_estimate * 1.2)  # Add 20% buffer
    print(f'Using gas: {gas_to_use}')
except Exception as e:
    print(f'Gas estimate error: {e}')
    gas_to_use = 400000

try:
    tx = validation.functions.postEIP712Attestation(33, checkpoint_hash, 75, 'test').build_transaction({
        'from': Web3.to_checksum_address(OPERATOR_WALLET),
        'nonce': w3.eth.get_transaction_count(Web3.to_checksum_address(OPERATOR_WALLET)),
        'gas': gas_to_use,
        'gasPrice': int(w3.eth.gas_price * 2),
        'chainId': 11155111
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=OPERATOR_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f'Tx sent: {tx_hash.hex()}')
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f'Tx status: {receipt.status}')
    print(f'Gas used: {receipt.gasUsed}')
    
    if receipt.status == 1:
        print('SUCCESS!')
        score = validation.functions.getAverageValidationScore(33).call()
        print(f'New score: {score}')
    else:
        print('FAILED - reverted')
except Exception as e:
    print(f'Error: {e}')
