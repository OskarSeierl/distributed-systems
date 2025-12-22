# Distributed Systems Project
**Erasmus 2025/26**

## Team Members
| Name | ID       | Email                     | GitHub        |
| --- |----------|---------------------------|---------------|
| Oskar Seierl | el25562  | oskar.seierl@tuwien.ac.at | `OskarSeierl` |
| Juan Gomez Rey | el25561  | jugorey@hotmail.com       | `Juangomezzr`|
| Member Three | Research | member3@example.com       | `member3`     |
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
TODO
#### Block
TODO
#### Blockchain
TODO
#### Dump
TODO
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
