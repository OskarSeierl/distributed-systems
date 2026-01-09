import argparse
import time
import matplotlib.pyplot as plt  

class NoobCashClient:
    def __init__(self, ip):
        self.ip = ip

    def send_transaction(self, sender, receiver, amount):
        start_time = time.time()

        print(f"Sending {amount} NBC from {sender} to {receiver}...")

        time.sleep(1.5)  # wait 1.5 seconds for the simulation

        end_time = time.time()

        transaction_time = end_time - start_time
        print(f"Transaction Time: {transaction_time} seconds")

        with open('transaction_data.txt', 'a') as file:
            file.write(f"Transaction Time: {transaction_time} seconds\n")

        return transaction_time  

    #def mine_block(self, transactions, difficulty):
    def mine_block(self, transactions):
        block_start_time = time.time()

        print(f"Mining block with transactions: {transactions}...")

        #time.sleep(difficulty)  # wait 6 seconds for the simulation 
        time.sleep(6)

        block_end_time = time.time()

        block_time = block_end_time - block_start_time
        print(f"Block Time: {block_time} seconds")

        with open('transaction_data.txt', 'a') as file:
            file.write(f"Block Time: {block_time} seconds\n")

        return block_time  

    # def run(self, difficulty=4):
    def run(self):
        transaction_times = []  
        block_times = []  

        # for node in range(5)
        for node in range(10):  
            transaction_time = self.send_transaction(f"Node {node}", f"Node {node+1}", 100)
            block_time = self.mine_block([{"from": f"Node {node}", "to": f"Node {node+1}", "amount": 100}], difficulty)
            transaction_times.append(transaction_time)
            block_times.append(block_time)

        
        nodes = list(range(10))  
        self.plot_graph(nodes, transaction_times, block_times)

    def plot_graph(self, nodes, transaction_times, block_times):
        # Transaction Time Graphic
        plt.figure(figsize=(10, 5))
        plt.plot(nodes, transaction_times, label="Transaction Time", color="blue", marker="o")
        plt.xlabel("Node ID")
        plt.ylabel("Transaction Time (second)")
        plt.title("Transaction Time vs. Node ID")
        plt.legend()
        plt.grid(True)
        plt.show()

        # Block Time Graphic
        plt.figure(figsize=(10, 5))
        plt.plot(nodes, block_times, label="Block Time", color="red", marker="x")
        plt.xlabel("Node ID")
        plt.ylabel("Block Time (second)")
        plt.title("Block Time vs. Node ID")
        plt.legend()
        plt.grid(True)
        plt.show()

# Main 
if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--ip", help="IP of the host", default="127.0.0.1")
    argParser.add_argument("--difficulty", help="Block mining difficulty", type=int, default=4)
    args = argParser.parse_args()

    client = NoobCashClient(args.ip)
    try:
        client.run(difficulty=args.difficulty)  
    except KeyboardInterrupt:
        print("\nGoodbye!")
