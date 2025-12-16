import json
from dotenv import load_dotenv
import os

from time import time
from Crypto.Hash import SHA256

from src.noobcash.blockchain import Blockchain
from src.utils.logger import Logger

load_dotenv()
block_size = int(os.getenv('BLOCK_SIZE'))
mining_difficulty = int(os.getenv('MINING_DIFFICULTY'))

class Block:
    def __init__(self, previous_hash):
        """
        Initialize a block.

        :param previous_hash: The hash of the previous block in the blockchain.
        """
        self.previous_hash = previous_hash
        self.timestamp = time()
        self.hash = None
        self.nonce = None
        self.transactions_list = []
	
    def calculate_hash(self):
        """
        Return hash of the block.

        :return: The calculated SHA256 hash of the block.
        """
        block_object = {
            'nonce': self.nonce,
            'timestamp': self.timestamp, 
            'transactions': [tr.transaction_id for tr in self.transactions_list],
            'previous_hash': self.previous_hash
        }
        
        block_dump = json.dumps(block_object.__str__())
        self.hash = SHA256.new(block_dump.encode("ISO-8859-2")).hexdigest()
        
        return self.hash
    
    def validate_block(self, blockchain: Blockchain):
        """
        Validate current_hash and previous_hash.
        Called from a node when it receives a broadcasted block (that isn't the genesis block).
        Checks 1) if current_hash is correct
               2) if the previous_hash field is equal to the the hash of the actual previous block

        :param blockchain: The blockchain instance to validate against.
        :return: True if the block is valid, False otherwise.
        """
        # Special case: If it is the genesis block, it's valid 
        if self.previous_hash == 1 and self.nonce == 0:
            return True
        
        # Get last block of the chain and check its hash
        prev_block = blockchain.chain[-1]
        
        # 1) Check if the previous_hash field is equal to the the hash of the actual previous block
        if self.previous_hash != prev_block.hash:
            Logger.error("Error in block validation: Not correct previous_hash")
            return False

        # 2) Check if current_hash is correct
        if self.hash.startswith('0' * blockchain.difficulty):
            Logger.success('Block validated !')
            return True
        else:
            Logger.error("Error in block validation: Not correct hash")
            return False
