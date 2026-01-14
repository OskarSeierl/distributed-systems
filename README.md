# Distributed Systems Project
**Erasmus 2025/26**

## Team Members
| Name | ID       | Email                     | GitHub        |
| --- |----------|---------------------------|---------------|
| Oskar Seierl | el25562  | oskar.seierl@tuwien.ac.at | `OskarSeierl` |
| Juan Gomez Rey | el25561  | jugorey@hotmail.com       | `Juangomezzr`|
| Fatma Zehra Aras | el25553 | fatmazehra.aras@stu.fsm.edu.tr       | `fzehraaras`     |
| Muhammed Gelgör | el25552 | Muhammed.gelgor@stu.fsm.edu.tr | `MGelgor`     |

## Usage
### Get Started
To start the project on a Windows machine, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/OskarSeierl/distributed-systems
2. Navigate to the project directory:
   ```bash
   cd distributed-systems
   ```
3. Install dependencies:
   ```bash
    python -m pip install -r requirements.txt
4. Run the nodes:
   ```bash
    ./start_nodes.ps1
5. Run the client:
   ```bash
    python -m src.client.client
   ```
   or visit `http://127.0.0.1:<port>` in your web browser to have an fancy web client.
       

6. Have fun with Noobcash!

### Start Single Node
To start a single node, use the following command:
```bash
python -m src.noobcash.api --port 8000
```

### Client
Using the client enables you to interact with the distributed system.
You can perform actions such as creating transactions, querying the blockchain, and more.

#### Web-Based
Open your web browser and visit `http://127.0.0.1:<port>`, e.g. http://127.0.0.1:8000

#### Terminal
Simply execute the client python script by running `python -m src.client.client` in your terminal.

### Automated Testing
To run the given tests in `testing/`, execute `python -m src.noobcash.test --nodes [5/10]`.
This will run all the test cases and save the results in a `.txt` file in the same folder.
Make sure that all nodes are running before executing the tests.

The result file will contain lines with the following format: [block_num], [current_time], [time_since_last_block].

## Environment Variables
- `API_IP`: The IP address for the API server
- `BOOTSTRAP_PORT`: The port for the bootstrap node
- `BLOCK_SIZE`: The maximum number of transactions per block
- `MINING_DIFFICULTY`: The difficulty level for mining

These variables can be set in a `.env` file or directly in the environment before running the application.

## Measurements
TODO

## Explanation of the Project
### Classes
#### Api
api.py is the network interface layer of the NoobCash system. It wraps a Node instance inside a Flask HTTP server and exposes REST endpoints so that:
	1.	Users / clients can create transactions and query the node’s state (balance, blockchain length, latest block transactions).
	2.	Nodes can communicate with each other by sending and receiving:
	•	the ring (peer registry),
	•	the blockchain,
	•	transactions,
	•	blocks.

This file is also responsible for bootstrapping logic: identifying whether a node is the bootstrap node, 
registering nodes to the cluster, creating the genesis block, 
and triggering the initial NBC distribution when all nodes have joined.
#### Block
The Block class represents a single block in the blockchain.

A block stores the hash of the previous block, a timestamp, a nonce used for Proof-of-Work, and a list of transactions. The block hash is generated using the calculate_hash() method, which computes a SHA-256 hash over the block’s nonce, timestamp, transaction identifiers, and previous block hash.

Mining is performed by repeatedly modifying the nonce and recomputing the hash until the hash satisfies the required difficulty (leading zeros).

The method validate_block(blockchain) is used when a block is received from another node. It verifies that:
	1.	the block correctly references the hash of the previous block in the chain, and
	2.	the block hash satisfies the Proof-of-Work difficulty.

A special case is handled for the genesis block, which is always considered valid.

#### Blockchain
The Blockchain class manages the local blockchain ledger and the state needed for validation and consensus.
	•	It stores the chain as a list of blocks (self.chain) and keeps configuration values such as mining difficulty (self.difficulty) and the maximum number of transactions per block (self.maxBlockTransactions), loaded from environment variables.
	•	It maintains the UTXO state in self.UTXOs (indexed by client_id) and tracks seen transactions using self.transactions_set to help prevent duplicates.

Key functions:
	•	validate_chain() iterates through the entire chain to verify integrity. It explicitly checks the genesis block (previous_hash = 1, nonce = 0) and calls each block’s validate_block(self) for all subsequent blocks.
	•	resolve_conflict(node) implements the consensus protocol (longest valid chain). It queries peers for /blockchain/length, selects the node with the longest chain, downloads it from /blockchain, and replaces the local blockchain if a longer one is found.
	•	wallet_balance(client_id) computes a wallet’s balance by summing the amounts of all UTXOs belonging to the given client ID.
#### Dump
The Dump class is used for performance evaluation and benchmarking of the blockchain system.

It records timing information during block creation in order to measure metrics such as block time and throughput under different configurations (number of nodes, block size, and mining difficulty).

The method timestamp() is called whenever a new block is processed. It:
	•	records the current time,
	•	computes the time elapsed since the previous block,
	•	and appends the block index, absolute timestamp, and block interval to a results file whose name encodes the experiment parameters.

This data is later used to analyze system performance and scalability.
#### Node
The Node class represents a participant in the NoobCash network. It combines the local wallet, blockchain state, UTXO management, mining logic, and all peer-to-peer communication.

Key responsibilities and functions:
	•	Local state & network metadata: Initializes a Wallet, a local Blockchain, and a ring registry ({address: {id, ip, port, balance}}). Nodes join the network via unicast_node() (register to bootstrap) and bootstrap maintains membership using add_node_to_ring().
	•	Block creation & transaction pool: Creates candidate blocks with create_new_block() and stores incoming/unconfirmed transactions in pending_transactions. New transactions are inserted through add_transaction_to_pending(), which also starts the mining thread when idle.
	•	Transaction creation & propagation: Builds signed transactions using create_transaction(receiver_address, amount), and propagates them to peers via broadcast_transaction(transaction).
	•	UTXO and balance updates: Maintains balances and UTXO sets. UTXOs are updated through _process_utxo_update() (shared helper), with update_original_utxos() applying confirmed changes and update_temp_utxos() applying changes to a temporary UTXO snapshot used during mining. Wallet/ring balances are updated with update_wallet_state(tx).
	•	Mining / Proof-of-Work: The mining loop runs in mine_process(). It validates pending transactions against temp_utxos, fills a block up to BLOCK_SIZE, and performs PoW using mine_block(block) (random nonce search until the hash meets MINING_DIFFICULTY). On success, it commits the block, updates state, records benchmarking data via dump.timestamp(), and broadcasts the block with broadcast_block(block).
	•	Receiving blocks and synchronization: When an externally mined block is accepted, add_block_to_chain(block) appends it, updates UTXOs and balances, removes mined transactions from the pending pool using update_pending_transactions(incoming_block), and resets mining flags/temporary state. Concurrency is handled using incoming_block_lock and processing_block_lock to coordinate mining vs incoming blocks.
	•	Bootstrap distribution: The bootstrap node can distribute the initial funds using broadcast_initial_nbc() / unicast_initial_nbc() after the ring is complete, ensuring each node receives its initial NBC balance.
#### Transaction
The Transaction class represents a transfer of NoobCoins between two wallets.

A transaction stores the sender and receiver wallet addresses, the transferred amount, a unique transaction identifier, and a cryptographic signature. The transaction ID is generated using calculate_hash(), which assigns a random unique value to each transaction.

To ensure authenticity, the transaction is signed using the sender’s private key via sign_transaction(private_key). The signature is created over a deterministic payload produced by get_sign_payload(), ensuring consistent hashing across nodes.

Signature verification is performed by verify_signature(), which uses the sender’s public key to confirm the transaction’s authenticity. Transaction validity is further checked using validate_transaction(utxo_id, utxos), which verifies both the signature and that the sender has sufficient funds based on the current UTXO set.

For serialization and logging, to_dict() provides a dictionary representation of the transaction.
#### UTXO
The UTXO (Unspent Transaction Output) class represents a single unspent output created by a transaction.

Each UTXO stores:
	•	the sender identifier,
	•	the receiver identifier (owner of the funds),
	•	and the amount of NoobCoins it represents.

UTXOs are used to track wallet balances and validate transactions. A wallet’s balance is computed as the sum of all UTXOs where it is the receiver. When a transaction is confirmed, the corresponding UTXOs are consumed and new UTXOs are created to reflect the transfer and any remaining change.
#### Wallet
The Wallet class represents a user’s identity and cryptographic account in the NoobCash system.

Each wallet generates a 2048-bit RSA key pair upon initialization. The private key is used to sign transactions, while the public key is exported and used as the wallet’s address. This address uniquely identifies the wallet within the network.

The wallet also maintains a local list of transactions associated with it, allowing the node to track incoming and outgoing transfers.

### General Description
This project implements NoobCash, a distributed cryptocurrency system based on a blockchain with Proof-of-Work consensus. Each node in the network operates independently while maintaining a consistent view of the ledger through block validation, transaction propagation, and conflict resolution.

At startup, one node acts as the bootstrap node, responsible for initializing the network, creating the genesis block, registering participating nodes, and distributing the initial NoobCoin (NBC) balances. All other nodes register with the bootstrap and receive the full network topology (ring) and blockchain state.

Each node maintains:
	•	a wallet with a public/private RSA key pair,
	•	a local copy of the blockchain,
	•	a UTXO set for balance tracking and transaction validation,
	•	a pool of pending transactions awaiting confirmation.

Transactions are digitally signed by the sender, validated using UTXOs, and broadcast to all nodes. Nodes collect valid transactions into blocks and perform Proof-of-Work mining by searching for a nonce that satisfies the configured difficulty. Newly mined blocks are broadcast to the network and independently validated by peers before being appended to their local chains.

To handle forks or inconsistencies, nodes apply a longest valid chain consensus mechanism. Performance metrics such as block creation time are recorded during execution to support experimental evaluation and scalability analysis.

## Problems Encountered
### Transaction Loss
An early issue was caused by removing transactions from the pending pool before a block was successfully mined.
When mining was interrupted by an incoming block from the network, these transactions were neither included in the blockchain nor reinserted into the pending pool, leading to lost transactions.

### Infinite Mining Loop
Another problem occurred when transactions became invalid due to changes in the UTXO set (e.g., insufficient funds after other transactions were confirmed).
Since invalid transactions were not removed from the pending pool, the miner repeatedly retried them, resulting in an infinite validation loop.

### State Inconsistency During Mining
Mining initially reused the global UTXO state, causing inconsistencies between transaction creation and validation.
This was resolved by introducing a temporary UTXO set for each mining round, ensuring that transaction validation during mining reflects a consistent and isolated state.



## Blockchain Performance and Scalability Analysis

This repository contains an in-depth performance and scalability analysis of the blockchain system, including tests with **1, 5, and 10 nodes** and varying **difficulty levels** (4 and 5).

### Key Highlights:
- **Transaction Time**: The time to process a transaction between nodes. The system performed efficiently, with minimal delay (~1.5 seconds).
- **Block Time**: The time to mine a block, which was consistent but increased slightly with higher difficulty levels.
- **Performance Test**: Conducted with **5 nodes** to evaluate the system's efficiency under typical conditions.
- **Scalability Test**: Conducted with **10 nodes**, showing minimal impact on performance as the number of nodes increased.
- **Difficulty Test**: Two difficulty levels (4 and 5) were tested, with **difficulty = 5** leading to slightly increased **block mining times**.

The complete analysis and results, including **graphs**, are detailed in the 'analysis_report.md'.

