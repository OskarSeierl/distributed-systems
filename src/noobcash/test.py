import time
import argparse
import requests
import random
import os
from threading import Thread
from dotenv import load_dotenv


def send_transactions(file_path, node_addr):
    """
    Worker function executed by each thread.
    Reads a transaction file line-by-line and sends requests to the specific node.
    """
    base_url = f'http://{node_addr}/api/create_transaction/'

    if not os.path.exists(file_path):
        print(f"Error: Transaction file not found: {file_path}")
        return

    print(f"Starting worker for {node_addr} using {file_path}")

    with open(file_path, 'r') as f:
        counter = 0
        for line in f:
            # Simulate user delay between typing transactions
            time.sleep(random.uniform(0.1, 0.5))

            # Limit to 20 transactions per node for this test run
            counter += 1
            if counter > 20:
                break

            parts = line.split()
            if len(parts) < 2:
                continue

            # PARSING LOGIC:
            # The file format is expected to be: "id{ID} {AMOUNT}" (e.g., "id8 5")
            # parts[0] is "id8". parts[0][2] extracts the character at index 2 ('8').
            try:
                receiver_id = int(parts[0][2])
                amount = int(parts[1])
            except (IndexError, ValueError):
                print(f"Skipping malformed line: {line.strip()}")
                continue

            # Simulate thinking time before hitting enter
            time.sleep(random.uniform(1, 2))

            # Construct the API endpoint: /api/create_transaction/<receiver_id>/<amount>
            request_url = f"{base_url}{receiver_id}/{amount}"
            print(f"Sending: {request_url}")

            try:
                response = requests.get(request_url)
                # Print response to confirm success or debug errors
                if response.status_code == 200:
                    print(f"Success: {response.json()}")
                else:
                    print(f"Failed ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Connection error to {node_addr}: {e}")


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

    print(f"--- CONFIGURATION ---")
    print(f"Nodes: {args.nodes}")
    print(f"Capacity: {capacity}")
    print(f"Difficulty: {difficulty}")
    print(f"Transaction Folder: {transaction_folder}")
    print(f"---------------------")

    with open(f'testing/results_{args.nodes}nodes.txt', 'a') as f:
        f.write(f'CAPACITY:{capacity}, DIFFICULTY:{difficulty}, NODES:{args.nodes}\n')

    # 3. Load Network Addresses
    # Generate localhost addresses: 127.0.0.1:8000, 127.0.0.1:8001, ...
    nodes = [f"127.0.0.1:{8000 + i}" for i in range(args.nodes)]

    # 4. Start Threads
    # We create one thread per node. Each thread reads its specific transaction file
    # and sends those transactions to its assigned node.
    threads = []
    print("Starting transaction threads...")

    for i, node_addr in enumerate(nodes):
        t = Thread(target=send_transactions, args=(f"{transaction_folder}/transactions{i}.txt", node_addr))
        threads.append(t)
        t.start()

    # 5. Wait for completion
    for t in threads:
        t.join()

    print("All transaction threads finished.")


if __name__ == "__main__":
    main()
