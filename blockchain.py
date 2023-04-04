from datetime import datetime
from hashlib import sha256
from flask import Flask, jsonify, request
import json

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({"index": self.index, "timestamp": str(self.timestamp), "transactions": self.transactions, "previous_hash": self.previous_hash, "nonce": self.nonce}, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 2

    def create_genesis_block(self):
        return Block(0, datetime.now(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def mine_pending_transactions(self, cargo):
        block = Block(len(self.chain), datetime.now(), self.pending_transactions, self.get_latest_block().hash)
        block.nonce = 0
        while not self.is_valid_proof(block, cargo):
            block.nonce += 1
        self.add_block(block)
        self.pending_transactions = []

    def is_valid_proof(self, block, cargo):
        return block.hash.startswith('0'*self.difficulty) and self.valid_votes(block.transactions, cargo)

    def valid_votes(self, transactions, cargo):
        for transaction in transactions:
            if transaction["cargo"] == cargo or transaction["delegado"] == cargo:
                if not self.valid_signature(transaction["dni"], transaction["archivo"]):
                    return False
            elif transaction["delegado"] == "" and transaction["cargo"] == cargo:
                if not self.valid_signature(transaction["dni"], transaction["archivo"]):
                    return False
        return True

    def valid_signature(self, dni, archivo):
        # Aquí debería ir la validación de la firma digital del archivo usando la clave pública del DNI
        return True

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/votar', methods=['POST'])
def votar():
    transaction_info = request.get_json()
    required_fields = ['dni', 'cargo', 'archivo']
    if not all(field in transaction_info for field in required_fields):
        return 'Falta información en la transacción', 400
    transaction_info['delegado'] = request.remote_addr #Guardamos la dirección IP del usuario
    blockchain.pending_transactions.append(transaction_info)
    return 'Transacción agregada a la cola de pendientes', 201

@app.route('/minar', methods=['GET'])
def minar():
    if not blockchain.pending_transactions:
        return 'No hay transacciones pendientes para minar', 400


    
    
