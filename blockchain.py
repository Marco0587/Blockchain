
import numpy as np
import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import requests


class Blockchain():

    def __init__(self):
        self.current_transactions = []
        self.chain = []

        self.nodes = set()

        # inizializzo la catena con il primo blocco
        self.add_block(proof = 100, previous_hash = '0'*64)
    

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    

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
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash.startswith('00')
    

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            # Check that the hash of the block is correct
            last_hash = self.hash(last_block)
            if block['previous_hash'] != last_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_hash):
                return False

            last_block = block
            block_index += 1

        return True


    def resolve_conflicts(self, logger):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        logger.info("DEBUG - dentro resolve_conflicts")

        neighbours = self.nodes
        logger.info("DEBUG - neighbours: {}".format(neighbours))
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            logger.info(f"DEBUG - node: {node} --> response: {response}")

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False