
import numpy as np
import json
import hashlib
from datetime import datetime

class Blockchain():
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.add_block(proof = 100, previous_hash = '0'*64)
    
    def add_block(self, proof, previous_hash = None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
        }

        self.current_transactions = []

        self.chain.append(block)
        return block
    
    def add_transaction(self, sender, recipient, amount):
        self.current_transactions.append(
            {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            }
        )
        return self.last_block['index']+1

    
    @staticmethod
    def hash(block):
        block_str = json.dumps(block, sort_keys=True).encode()
        h = hashlib.sha256(block_str)
        return h.hexdigest()

    
    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof +=1
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = "{}{}{}".format(last_proof, proof, last_hash).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash.startswith('00')