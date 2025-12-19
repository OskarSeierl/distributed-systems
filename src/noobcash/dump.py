import time

class Dump:
    def __init__(self, total_nodes: int, block_size: int, difficulty: int):
        """
        Initialize the Dump class for benchmarking.

        :param total_nodes: The total number of nodes in the network.
        """
        self.prev_timestamp = None
        self.block = None
        self.total_nodes = total_nodes
        self.block_size = block_size
        self.difficulty = difficulty

    def timestamp(self):
        """
        Record a timestamp for the current block processing time.
        Writes the block number, current time, and time elapsed since the last block to a file.

        :return: None
        """
        current = time.time()

        if self.block is None:
            self.block = 0
            self.prev_timestamp = current

        timestamp = current - self.prev_timestamp

        with open(f"testing/results/results_{self.total_nodes}nodes_{self.block_size}blocksize_{self.difficulty}difficulty.txt", "a") as f:
            f.write(f"{self.block}, {current}, {timestamp}\n")

        self.block += 1
        self.prev_timestamp = current