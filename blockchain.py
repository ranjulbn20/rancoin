# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.postman.com/

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Building a Blockchain

class Blockchain:
    
    def __init__(self):
        
        # Reset the current list of transactions
        self.chain = []
        
        # Create the genesis block
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        """
        Create a new block in the Blockchain
        
        Each block includes:
            * Index
            * Timestamp
            * Proof
            * Previous Hash
            
            :param proof: The proof given by the Proof of Work algorithm
            :param previous_hash: Hash of the previous block
            :return new block
        """
        
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        """
        Simple Proof of Work Algorithm:
            
            - Find a number p such that hash(p^2 - q^2) contains leading 4 zeroes
            - Where q is the previous proof and p is the new proof
            
            :param previous_proof: <int> proof of the previos block
            :return: <int>
        """
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                
        return new_proof
    
    def hash(self, block):
        """
        Create a SHA-256 hash of a block
        
        :param block: Block
        :return hash value of the block
        """
        
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        """
        Performs two checks for validating the chain:
            
            - If the hash of the previous block matches with the previous_hash stored in the current block
            - If the hash of the current block contains leading 4 zeroes
            
        :param chain: A blockchain
        :return: <bool> True if valid, False if not
        """        
        # To check the validity of the chain we start from the first block
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            
            # First check
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            #Second Check
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
            
        return True

# Mining our Blockchain
        
# Web App
# Instantiate the Node
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating the Blockchain
blockchain = Blockchain()

# Mining a new Block
@app.route('/mine_block', methods = ['GET'])

def mine_block():
    
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    
    # Running the proof of work to get the new proof
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # New block is added to the chain
    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message': 'Congratulations on mining your block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    
    return jsonify(response), 200
    
# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])

def get_chain():
    
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return jsonify(response), 200

# Checking the blockchain
@app.route('/is_valid', methods = ['GET'])

def is_valid():
    
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {'message': 'Blockchain is valid.'}
    else:
        response = {'message': 'Blockchain is invalid.'}
        
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5000)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    