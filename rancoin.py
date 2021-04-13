# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.postman.com/
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Building a Blockchain

class Blockchain:
    
    def __init__(self):
        
        # Create an empty chain
        self.chain = []
        
        # Create an empty list of transactions
        self.transactions = []
        
        # Create the genesis block
        self.create_block(proof = 1, previous_hash = '0')
        
        #Create a empty set of nodes
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        """
        Create a new block in the Blockchain
        
        Each block includes:
            * Index
            * Timestamp
            * Proof
            * Previous Hash
            * Transactions
            
            :param proof: The proof given by the Proof of Work algorithm
            :param previous_hash: Hash of the previous block
            :return new block
        """
        
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        
        # Reset the current list of transactions
        self.transactions = []
        
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
    
    def add_transaction(self, sender, receiver, amount):
        """
        Add transaction to the transaction list
        
        :param sender:
        :param receiver:
        :param amount: Amount of rancoin exchanged
        :return index of the new block which will contain the transactions
        """
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        
        return previous_block['index'] + 1

    def add_node(self, address):
        """
        Add a node containing an address to the set of nodes
        
        :param address: address of the node
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        """
        Implementaion of the Consensus Algorithm:
            - replace any chain which is shorter than the longest chain among 
              all the nodes in the network  
              
        :return: <bool> True if chain is replaced, False if not
        """
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            
            response = requests.get(f'http://{node}/get_chain')
            
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                #Replace max_length and longest_chain if length of the current node is greater and the chain is valid
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    
        if longest_chain:
            self.chain = longest_chain
            return True
        
        return False
            
# Mining our Blockchain
        
# Web App
# Instantiate the Node
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

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
    
    #Add transactions to the blockchain
    blockchain.add_transaction(sender = node_address, receiver = 'User', amount = 0.1)
    
    # New block is added to the chain
    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message': 'Congratulations on mining your block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
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

#Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])

def add_transaction():
    
    json = request.get_json()
    
    transaction_keys = ['sender', 'receiver', 'amount']
    
    #Check if there is a missing key
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing' , 400
    
    #If there is no key missing then add transaction to the next block
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    
    response = {'message': f'This transaction will be added to Block {index}'}
    
    return jsonify(response), 201

# Decentralising the blockchain

#Connecting new nodes
@app.route('/connect_node', methods = ['POST'])

def connect_node():
    
    json = request.get_json()
    
    nodes = json.get('nodes')
    
    #Check if nodes list is not empty
    if nodes is None:
        return "No node", 400
    
    #Adding nodes into the blockchain    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message': 'All the nodes are now connected. The Rancoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    
    return jsonify(response), 201
    
#Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])

def replace_chain():
    
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        response = {'message': 'The chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The chain is the largest one.',
                    'actual_chain': blockchain.chain}
        
    return jsonify(response), 200
    
# Running the app
app.run(host = '0.0.0.0', port = 5000)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

