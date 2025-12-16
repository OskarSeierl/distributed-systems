# Distributed Systems Project
**Erasmus 2025/26**

## Team Members
| Name | ID       | Email                     | GitHub        |
| --- |----------|---------------------------|---------------|
| Oskar Seierl | el25562  | oskar.seierl@tuwien.ac.at | `OskarSeierl` |
| Member Two | Backend  | member2@example.com       | `member2`     |
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
To run the given tests in `testing/`, execute `python src/noobcash/test.py`.
This will run all the test cases and save the results in a `.txt` file in the same folder.
Make sure that all nodes are running before executing the tests.

## Environment Variables
- `API_IP`: The IP address for the API server
- `BOOTSTRAP_PORT`: The port for the bootstrap node
- `BLOCK_SIZE`: The maximum number of transactions per block
- `MINING_DIFFICULTY`: The difficulty level for mining

These variables can be set in a `.env` file or directly in the environment before running the application.

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

### Measurements
TODO

__!!! TODO !!!__
EXPLAIN ALL THE DIFFERENT PYTHON CLASSES AND THE GENERAL ARCHITECTURE OF THE PROJECT

