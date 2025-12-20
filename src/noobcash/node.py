from collections import deque
from copy import deepcopy
from dotenv import load_dotenv
import requests
import pickle
import os
import random
import threading

from src.noobcash.block import Block
from src.noobcash.blockchain import Blockchain
from src.noobcash.dump import Dump
from src.noobcash.transaction import Transaction
from src.noobcash.utxo import UTXO
from src.noobcash.wallet import Wallet
from src.utils.logger import Logger

load_dotenv()
BLOCK_SIZE = int(os.getenv('BLOCK_SIZE', 5))
MINING_DIFFICULTY = int(os.getenv('MINING_DIFFICULTY', 4))


class Node:
    def __init__(self, total_nodes: int):
        """
        Initialize a Node with a wallet, blockchain, and network ring.

        :param total_nodes: The total number of nodes in the network for benchmarking.
        """
        self.wallet = Wallet()
        self.ip = None
        self.port = None
        self.id = None
        self.ring = {}  # {address: {id, ip, port, balance}}
        self.blockchain = Blockchain()
        self.is_bootstrap = False
        self.current_block = None
        self.is_mining = False
        self.incoming_block = False
        self.processing_block = False
        self.pending_transactions = deque()
        self.temp_utxos = None

        self.incoming_block_lock = threading.Lock()
        self.processing_block_lock = threading.Lock()
        self.dump = Dump(total_nodes, BLOCK_SIZE, MINING_DIFFICULTY)

    # --- Block & Transaction Management ---

    def create_new_block(self):
        """
        Creates a new block for the blockchain, linking it to the previous hash.

        :return: The newly created Block instance.
        """
        prev_hash = 1 if not self.blockchain.chain else self.blockchain.chain[-1].hash
        self.current_block = Block(prev_hash)
        return self.current_block

    def add_transaction_to_pending(self, transaction: Transaction):
        """
        Adds a transaction to the pool and starts the mining thread if idle.

        :param transaction: The Transaction object to be added.
        """
        self.pending_transactions.appendleft(transaction)
        if self.current_block is None:
            self.create_new_block()

        if not self.is_mining:
            mining_thread = threading.Thread(
                target=self.mine_process,
                daemon=True,
                name="MinerThread"
            )
            mining_thread.start()

    # --- State & UTXO Management ---

    def update_wallet_state(self, tx: Transaction):
        """
        Updates the internal balances in the ring and local wallet transaction history.
        Logs the transaction with a clear visual separator.

        :param tx: The validated Transaction to process.
        """
        sender_addr = str(tx.sender_address)
        receiver_addr = str(tx.receiver_address)

        if tx.receiver_address == self.wallet.address or tx.sender_address == self.wallet.address:
            self.wallet.transactions.append(tx)

        sender_id = self.ring[sender_addr]['id']
        receiver_id = self.ring[receiver_addr]['id']

        self.ring[sender_addr]['balance'] -= tx.amount
        self.ring[receiver_addr]['balance'] += tx.amount

        # Single-line transaction log
        Logger.info(
            f"New Transaction | {sender_id} --> {receiver_id} | {tx.amount}NBC"
        )

    def _process_utxo_update(self, utxo_set, tx: Transaction):
        """
        Internal helper to update a specific UTXO set based on transaction flow.

        :param utxo_set: The UTXO dictionary to modify (temp or original).
        :param tx: The transaction causing the UTXO movement.
        """
        s_addr, r_addr = str(tx.sender_address), str(tx.receiver_address)
        s_id, r_id = self.ring[s_addr]['id'], self.ring[r_addr]['id']

        # Credit receiver
        utxo_set[r_id].append(UTXO(s_id, r_id, tx.amount))

        # Debit sender
        accumulated = 0
        while accumulated < tx.amount:
            try:
                utxo = utxo_set[s_id].popleft()
                accumulated += utxo.amount
            except IndexError:
                Logger.error(f"UTXO Critical Error: Node {s_id} has insufficient funds.")
                break

        # Change handling
        if accumulated > tx.amount:
            utxo_set[s_id].append(UTXO(s_id, s_id, accumulated - tx.amount))

    def update_original_utxos(self, tx: Transaction):
        """
        Updates the authoritative UTXO set in the blockchain.

        :param tx: The validated Transaction to process.
        """
        self._process_utxo_update(self.blockchain.UTXOs, tx)

    def update_temp_utxos(self, tx: Transaction):
        """
        Updates the temporary UTXO set used during the mining of the current block.

        :param tx: The Transaction to process.
        """
        self._process_utxo_update(self.temp_utxos, tx)

    # --- Mining Logic ---

    def mine_process(self):
        """
        Main mining loop.
        - Uses temp UTXOs
        - Does NOT lose transactions
        - Drops permanently invalid transactions
        - Safely handles incoming blocks
        """

        self.is_mining = True

        # 🔑 Initialize temporary UTXO state for this mining round
        self.temp_utxos = deepcopy(self.blockchain.UTXOs)

        while self.pending_transactions:

            Logger.info(
                "Pending Transaction: " +
                self.transaction_to_string(self.pending_transactions)
            )

            # Peek — do NOT remove yet
            tx = self.pending_transactions[-1]

            # Already confirmed elsewhere → drop
            if tx.transaction_id in self.blockchain.transactions_set:
                self.pending_transactions.pop()
                continue

            sender_id = self.ring[str(tx.sender_address)]['id']

            # Permanently invalid → drop
            if not tx.validate_transaction(sender_id, self.temp_utxos):
                Logger.error("Transaction NOT Validated: Not enough coins — dropping")
                self.pending_transactions.pop()
                continue

            # Valid transaction -> tentatively add to block
            self.current_block.transactions_list.append(tx)
            self.update_temp_utxos(tx)
            self.pending_transactions.pop()

            # Block full -> mine it
            if len(self.current_block.transactions_list) == BLOCK_SIZE:

                Logger.mining(
                    f"Block Full. Starting Proof-of-Work for transactions: "
                    f"{self.transaction_to_string(self.current_block.transactions_list)}"
                )

                mined = self.mine_block(self.current_block)

                with self.processing_block_lock:

                    # Mining succeeded and no conflicting block arrived
                    if mined and not self.incoming_block and \
                            self.current_block.validate_block(self.blockchain):

                        Logger.mining(
                            f"Block mined successfully | Miner: Node {self.id} | "
                            f"Hash: {self.current_block.hash[:15]}... | "
                            f"Transactions: {len(self.current_block.transactions_list)} | "
                            f"Nonce: {self.current_block.nonce}"
                        )

                        # Commit block
                        self.blockchain.chain.append(self.current_block)
                        self.blockchain.UTXOs = deepcopy(self.temp_utxos)

                        for t in self.current_block.transactions_list:
                            self.update_wallet_state(t)
                            self.blockchain.transactions_set.add(t.transaction_id)

                        self.dump.timestamp()
                        self.broadcast_block(self.current_block)

                    # Either mined by someone else or interrupted
                    else:
                        Logger.mining("Mining aborted — block mined elsewhere")

                # Prepare new block regardless of outcome
                self.create_new_block()
                self.temp_utxos = deepcopy(self.blockchain.UTXOs)

        self.is_mining = False

    def mine_block(self, block: Block):
        """
        Performs the Proof-of-Work by iterating nonces until the difficulty target is met.

        :param block: The Block instance to mine.
        :return: True if a nonce was found, False if mining was interrupted by an incoming block.
        """
        target = '0' * MINING_DIFFICULTY
        while not self.incoming_block:
            block.nonce = random.getrandbits(32)
            if block.calculate_hash().startswith(target):
                return True

        Logger.mining("Mining interrupted by network broadcast.")
        return False

    def update_pending_transactions(self, incoming_block: Block):
        """
        Synchronizes the pending transaction pool with an incoming validated block.

        :param incoming_block: The Block received from the network.
        """
        for tx in self.current_block.transactions_list:
            if tx.transaction_id not in self.blockchain.transactions_set:
                self.pending_transactions.append(tx)

        mined_ids = {tx.transaction_id for tx in incoming_block.transactions_list}
        self.pending_transactions = deque([t for t in self.pending_transactions if t.transaction_id not in mined_ids])

    def add_block_to_chain(self, block: Block):
        """
        Appends an externally mined block to the local chain and updates state.

        :param block: The validated Block instance to add.
        """
        self.blockchain.chain.append(block)
        for tx in block.transactions_list:
            self.update_original_utxos(tx)
            self.update_wallet_state(tx)
            self.blockchain.transactions_set.add(tx.transaction_id)

        self.temp_utxos = deepcopy(self.blockchain.UTXOs)
        self.update_pending_transactions(block)
        self.dump.timestamp()

        Logger.info(f"Chain height increased: {len(self.blockchain.chain)}")
        with self.incoming_block_lock:
            self.incoming_block = False

    # --- Networking: Common ---

    def create_transaction(self, receiver_address, amount):
        """
        Creates, signs, and hashes a new transaction.

        :param receiver_address: The public key address of the recipient.
        :param amount: The amount of NBC to transfer.
        :return: A signed and hashed Transaction instance.
        """
        tx = Transaction(self.wallet.address, self.wallet.private_key, receiver_address, amount)
        tx.sign_transaction(self.wallet.private_key)
        tx.calculate_hash()
        return tx

    def broadcast_transaction(self, transaction):
        """
        Broadcasts a transaction to all nodes in the ring.

        :param transaction: The Transaction instance to broadcast.
        """
        for node in self.ring.values():
            if node['id'] != self.id:
                url = f"http://{node['ip']}:{node['port']}/transactions/receive"
                try:
                    requests.post(url, data=pickle.dumps(transaction), timeout=5)
                except requests.exceptions.RequestException:
                    Logger.error(f"Network Error: Could not broadcast TX to Node {node['id']}")

    def unicast_block(self, node, block):
        """
        Sends a block to a single node.

        :param node: The node dictionary.
        :param block: The Block object.
        """
        url = f"http://{node['ip']}:{node['port']}/blocks/receive"
        try:
            requests.post(url, data=pickle.dumps(block), timeout=5)
        except requests.exceptions.RequestException as e:
            Logger.error(f"Failed to unicast block to Node {node.get('id', '?')}, because of: {e}")

    def broadcast_block(self, block: Block):
        """
        Sends a newly mined block to all other nodes in the ring.

        :param block: The Block instance to broadcast.
        """
        for node in self.ring.values():
            if node['id'] != self.id:
                self.unicast_block(node, block)

    # --- Networking: Bootstrap & Initialization ---

    def unicast_node(self, node):
        """
        Sends information about self to the bootstrap node to register.

        :param node: The bootstrap node dictionary containing IP and port.
        """
        url = f"http://{node['ip']}:{node['port']}/nodes/register"
        try:
            response = requests.post(url, data={
                'ip': self.ip,
                'port': self.port,
                'address': self.wallet.address
            })
            if response.status_code == 200:
                self.id = response.json()['id']
                Logger.success(f"Registered with Bootstrap. Assigned ID: {self.id}")
            else:
                Logger.error(f"Registration failed: {response.text}")
        except requests.exceptions.RequestException as e:
            Logger.error(f"Connection error to Bootstrap node: {e}")

    def add_node_to_ring(self, id, ip, port, address, balance):
        """
        Adds a new node's metadata to the local ring.

        :param id: Numeric ID of the node.
        :param ip: IP address.
        :param port: Listening port.
        :param address: Wallet public key.
        :param balance: Initial balance.
        """
        self.ring[str(address)] = {'id': id, 'ip': ip, 'port': port, 'balance': balance}
        self.blockchain.UTXOs.append(deque())
        Logger.success(f"Node {id} synchronized to ring.")

    def unicast_ring(self, node):
        """
        Sends the ring (network topology) to a specific node.

        :param node: The target node dictionary.
        """
        url = f"http://{node['ip']}:{node['port']}/ring/receive"
        try:
            requests.post(url, data=pickle.dumps(self.ring))
        except requests.exceptions.RequestException:
            Logger.error(f"Failed to send ring to Node {node.get('id', 'Unknown')}")

    def broadcast_ring(self):
        """
        Broadcasts the updated ring to all nodes (Bootstrap only).
        """
        for node in self.ring.values():
            if self.id != node['id']:
                self.unicast_ring(node)
        Logger.network("Network ring broadcasted to all nodes.")

    def unicast_blockchain(self, node):
        """
        Sends the current blockchain state to a specific node.

        :param node: The target node dictionary.
        """
        url = f"http://{node['ip']}:{node['port']}/blockchain/receive"
        try:
            requests.post(url, data=pickle.dumps(self.blockchain))
        except requests.exceptions.RequestException:
            Logger.error(f"Failed to send blockchain to Node {node.get('id', 'Unknown')}")

    def broadcast_blockchain(self):
        """
        (Bootstrap Only) Broadcasts the current blockchain state to all peers.
        """
        self.temp_utxos = deepcopy(self.blockchain.UTXOs)
        for node in self.ring.values():
            if node['id'] != self.id:
                self.unicast_blockchain(node)
        Logger.network("Global Blockchain State Broadcasted.")

    def unicast_initial_nbc(self, node_address):
        """
        Creates and broadcasts an initial transaction of 100 NBC to a specific node.

        :param node_address: The public address of the recipient node.
        """
        # Create initial transaction (100 noobcoins)
        transaction = self.create_transaction(node_address, 100)
        self.add_transaction_to_pending(transaction)
        self.broadcast_transaction(transaction)
        Logger.network(f"Initial 100 NBC sent to Node Address {str(node_address)[:10]}...")

    def broadcast_initial_nbc(self):
        """
        Distributes initial 100 NBC to all registered nodes in the ring.
        """
        for node_address in self.ring:
            if self.id != self.ring[node_address]['id']:
                self.unicast_initial_nbc(node_address)
        Logger.network("Initial NBC distribution complete.")

    def transaction_to_string(self, transactions):
        """
        Returns a string representation of pending transactions for logging.

        :return: A formatted string of pending transactions.
        """
        tx_strings = []
        for tx in transactions:
            sender_id = self.ring[str(tx.sender_address)]['id']
            receiver_id = self.ring[str(tx.receiver_address)]['id']
            tx_strings.append(f"({sender_id} -> {receiver_id}: {tx.amount} NBC)")
        return ", ".join(tx_strings)