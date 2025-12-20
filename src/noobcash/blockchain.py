from dotenv import load_dotenv
import requests
import pickle
import os
from src.utils.logger import Logger
from copy import deepcopy

load_dotenv()
BLOCK_SIZE = int(os.getenv('BLOCK_SIZE'))
MINING_DIFFICULTY = int(os.getenv('MINING_DIFFICULTY'))

class Blockchain:
    def __init__(self):
        """
        Initialize a Blockchain instance.
        """
        self.chain = []  # List of Block objects representing the blockchain ledger
        self.difficulty = MINING_DIFFICULTY  # Mining difficulty level for proof-of-work
        self.maxBlockTransactions = BLOCK_SIZE  # Maximum transactions per block
        self.UTXOs = []  # List of UTXO lists, indexed by client_id
        self.transactions_set = set()  # Set of transaction IDs to prevent duplicates

    def validate_chain(self):
        """
        Validates the integrity of the entire blockchain.
        Checks the Genesis block explicitly and validates subsequent blocks against the chain history.

        :return: True if the chain is valid, False otherwise.
        """
        for i, block in enumerate(self.chain):
            # Special case: Genesis Block validation
            if i == 0:
                if block.previous_hash != 1 or block.nonce != 0:
                    return False
            # Standard Block validation
            else:
                if not block.validate_block(self):
                    return False
        return True

    @staticmethod
    def resolve_conflict(node):
        """
        Consensus Algorithm: Resolves conflicts by replacing the local chain with the
        longest valid chain found in the network.

        :param node: The node instance initiating the conflict resolution.
        """
        Logger.warning("Conflict Detected: Initiating Consensus Protocol...")

        current_max_length = len(node.blockchain.chain)
        best_node = None

        # 1. Query all other nodes for their chain length
        for peer in node.ring.values():
            if peer['id'] != node.id:
                try:
                    url = f"http://{peer['ip']}:{peer['port']}/blockchain/length"
                    response = requests.get(url, timeout=3)

                    if response.status_code == 200:
                        peer_length = response.json().get('chain_length', 0)

                        if peer_length > current_max_length:
                            current_max_length = peer_length
                            best_node = peer
                            Logger.network(f"Found longer chain candidate at Node {peer['id']} (Len: {peer_length})")
                except requests.exceptions.RequestException:
                    Logger.error(f"Consensus Error: Could not reach Node {peer['id']}")

        # 2. Evaluate results
        if best_node:
            Logger.info(f"Downloading new chain from Node {best_node['id']}...")

            # 3. Fetch the new chain
            try:
                url = f"http://{best_node['ip']}:{best_node['port']}/blockchain"
                response = requests.get(url, timeout=10)
                new_chain = pickle.loads(response.content)

                # 4. Replace local chain
                node.blockchain = new_chain

                Logger.success(
                    f"Chain replaced | Source: Node {best_node['id']} | New Length: {len(node.blockchain.chain)}"
                )
                return

            except Exception as e:
                Logger.error(f"Failed to download chain from Node {best_node['id']}: {e}")

        else:
            Logger.success("Local chain is authoritative. No changes made.")

    def wallet_balance(self, client_id):
        """
        Calculates the total balance for a specific wallet by summing its UTXOs.

        :param client_id: The ID of the client (node) to check.
        :return: The total float balance of the client.
       """
        balance = 0.0
        try:
            # Ensure the client_id exists in the UTXO list
            if client_id < len(self.UTXOs):
                for utxo in self.UTXOs[client_id]:
                    balance += utxo.amount
        except IndexError:
            Logger.error(f"Wallet Check Error: Client ID {client_id} not found in UTXOs.")

        return balance