import hashlib
import json
import time
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet

# Define la estructura del bloque
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calcular_hash()

    def calcular_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

# Crea la cadena de bloques
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.cargos_electos = {}
        self.key = Fernet.generate_key()

    def create_genesis_block(self):
        return Block(0, [], time.time(), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calcular_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calcular_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def votar(self, dni, cargo, archivo, delegado=None):
        # Comprobar si el DNI ya ha votado
        for block in self.chain:
            for transaction in block.transactions:
                if dni == transaction['dni']:
                    return {'error': 'Este DNI ya ha votado'}

        # Cifrar el archivo y la transacción con la clave secreta
        f = Fernet(self.key)
        encrypted_archivo = f.encrypt(archivo.encode()).decode()
        if delegado is None:
            transaction = {'dni': dni, 'cargo': cargo, 'archivo': encrypted_archivo}
        else:
            transaction = {'dni': delegado, 'cargo': cargo, 'archivo': encrypted_archivo, 'delegado_por': dni}
        encrypted_transaction = f.encrypt(json.dumps(transaction).encode()).decode()

        # Agregar la transacción a la cadena de bloques
        index = len(self.chain)
        new_block = Block(index, [encrypted_transaction], time.time(), "")
        self.add_block(new_block)

        # Agregar el candidato al cargo electo
        if cargo in self.cargos_electos:
            self.cargos_electos[cargo].append(dni)
        else:
            self.cargos_electos[cargo
