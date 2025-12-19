import time
import argparse
import requests
import random
import os
from threading import Thread
from dotenv import load_dotenv

from src.utils.logger import Logger


def send_transactions(file_path, node_addr):
    """
    Worker function executed by each thread.
    Reads a transaction file line-by-line and sends requests to the specific node.
    """
    base_url = f'http://{node_addr}/api/create_transaction/'

    if not os.path.exists(file_path):
        Logger.error(f"Transaction file not found: {file_path}")
        return

    Logger.info(f"Starting worker for {node_addr} using {file_path}")

    with open(file_path, 'r') as f:
        for line in f:
            # Simulate user delay between typing transactions
            time.sleep(random.uniform(0.1, 0.5))

            parts = line.split()

            # PARSING LOGIC:
            # The file format is expected to be: "id{ID} {AMOUNT}" (e.g., "id8 5")
            # parts[0] is "id8". parts[0][2] extracts the character at index 2 ('8').
            try:
                receiver_id = int(parts[0][2])
                amount = int(parts[1])
            except (IndexError, ValueError):
                Logger.warning(f"Skipping malformed line: {line.strip()}")
                continue

            # Simulate thinking time before hitting enter
            time.sleep(random.uniform(1, 2))

            # Construct the API endpoint: /api/create_transaction/<receiver_id>/<amount>
            request_url = f"{base_url}{receiver_id}/{amount}"
            Logger.info(f"Sending: {request_url}")

            try:
                response = requests.get(request_url)
                # Print response to confirm success or debug errors
                if response.status_code == 200:
                    Logger.success(f"Success: {response.json()}")
                else:
                    Logger.error(f"Failed ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                Logger.error(f"Connection error to {node_addr}: {e}")


def main():
    # 1. Parse Arguments
    parser = argparse.ArgumentParser(description="Run blockchain transaction tests.")
    parser.add_argument(
        "-n", "--nodes",
        help="Number of nodes in the network (e.g., 5 or 10)",
        type=int,
        required=True,
        choices=[5, 10]
    )
    args = parser.parse_args()

    # 2. Setup Environment & Paths
    load_dotenv()

    # Derive path based on node count. 
    # Assumes folder structure: testing/5_nodes/ or testing/10_nodes/
    transaction_folder = f"testing/{args.nodes}nodes"

    # Log configuration for reproducibility
    capacity = os.getenv('BLOCK_SIZE', 'Unknown')
    difficulty = os.getenv('MINING_DIFFICULTY', 'Unknown')
    bootstrap_port = os.getenv('BOOTSTRAP_PORT')

    Logger.info(f"--- CONFIGURATION ---")
    Logger.info(f"Nodes: {args.nodes}")
    Logger.info(f"Capacity: {capacity}")
    Logger.info(f"Difficulty: {difficulty}")
    Logger.info(f"Transaction Folder: {transaction_folder}")
    Logger.info(f"---------------------")

    with open(f'testing/results/results_{args.nodes}nodes_{capacity}blocksize_{difficulty}difficulty.txt', 'a') as f:
        f.write(f'CAPACITY:{capacity}, DIFFICULTY:{difficulty}, NODES:{args.nodes}\n')

    # 3. Load Network Addresses
    # Generate localhost addresses: 127.0.0.1:8000, 127.0.0.1:8001, ...
    nodes = [f"127.0.0.1:{int(bootstrap_port) + i}" for i in range(args.nodes)]

    # 4. Start Threads
    # We create one thread per node. Each thread reads its specific transaction file
    # and sends those transactions to its assigned node.
    threads = []
    Logger.info("Starting transaction threads...")

    for i, node_addr in enumerate(nodes):
        t = Thread(
            target=send_transactions,
            name=f"Worker-{i}",
            args=(f"{transaction_folder}/transactions{i}.txt", node_addr)
        )
        threads.append(t)
        t.start()

    # 5. Wait for completion
    for t in threads:
        t.join()

    Logger.info("All transaction threads finished.")

if __name__ == "__main__":
    main()
