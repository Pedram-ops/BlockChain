import os
import hashlib
import json
from datetime import datetime

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        transactions_str = ''.join([f'{t.sender}->{t.recipient}:{t.amount}' for t in self.transactions])
        value = f'{self.index}{self.previous_hash}{self.timestamp}{transactions_str}{self.nonce}'.encode()
        return hashlib.sha256(value).hexdigest()

    def mine_block(self, difficulty):
        required_prefix = '0' * difficulty
        while not self.hash.startswith(required_prefix):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "transactions": [
                {
                    "sender": tx.sender,
                    "recipient": tx.recipient,
                    "amount": tx.amount
                }
                for tx in self.transactions
            ],
            "nonce": self.nonce
        }

class Blockchain:
    def __init__(self, difficulty=5):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions = []
        self.mining_reward = 100
        self.block_file_prefix = "block"
        self.directory = "blocks"  # Directory to store block files
        self.create_directory()  # Create directory if it doesn't exist

    def create_directory(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def create_genesis_block(self):
        return Block(0, str(datetime.now()), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction("System", mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)

        new_block = Block(len(self.chain), str(datetime.now()), self.pending_transactions, self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)

        self.chain.append(new_block)
        self.pending_transactions = []
        
        self.log_block(new_block)  # Log the newly mined block
        self.save_block_to_file(new_block)  # Save block to a txt file

    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def get_balance_of_address(self, address):
        balance = 0
        for block in self.chain:
            for trans in block.transactions:
                if trans.sender == address:
                    balance -= trans.amount
                if trans.recipient == address:
                    balance += trans.amount
        return balance

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def log_chain(self):
        for block in self.chain:
            print("Index:", block.index)
            print("Timestamp:", block.timestamp)
            print("Previous Hash:", block.previous_hash)

            print("Hash:", block.hash)
            print("Transactions:")
            for trans in block.transactions:
                print(f"  {trans.sender} -> {trans.recipient}: {trans.amount}")
            print("Nonce:", block.nonce)
            print('-' * 120)
    
    def log_block(self, block):
        print("Block mined:")
        print("Index:", block.index)
        print("Timestamp:", block.timestamp)
        print("Previous Hash:", block.previous_hash)
        print("Hash:", block.hash)
        print("Transactions:")
        for trans in block.transactions:
            print(f"  {trans.sender} -> {trans.recipient}: {trans.amount}")
        print("Nonce:", block.nonce)
        print('-' * 120)

    def save_block_to_file(self, block):
        file_name = f"{self.directory}/{self.block_file_prefix}_{block.index}.txt"
        with open(file_name, 'w') as file:
            file.write(json.dumps(block.to_dict(), indent=4))

# Usage example to generate 100 blocks and log each one
blockchain = Blockchain()

while True:
    blockchain.create_transaction(Transaction("Sender", "Recipient", 10))
    blockchain.mine_pending_transactions("Miner")

# Check balance and validate chain
print("Balance of Miner:", blockchain.get_balance_of_address("Miner"))
print("Is chain valid?", blockchain.is_chain_valid())
blockchain.log_chain()