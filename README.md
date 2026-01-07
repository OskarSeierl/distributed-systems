# Distributed Systems Project
**Erasmus 2025/26**

## Team Members
| Name | ID       | Email                     | GitHub        |
| --- |----------|---------------------------|---------------|
| Oskar Seierl | el25562  | oskar.seierl@tuwien.ac.at | `OskarSeierl` |
| Juan Gomez Rey | el25561  | jugorey@hotmail.com       | `Juangomezzr`|
| Fatma Zehra Aras | el25553 | fatmazehra.aras@stu.fsm.edu.tr       | `fzehraaras`     |
| Member Three | Research | member3@example.com       | `member3`     |

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
TODO
#### Transaction
TODO
#### UTXO
TODO
#### Wallet
TODO

### General Description
TODO

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
