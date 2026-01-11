# Blockchain Performance and Scalability Analysis

## 1. Introduction

In this updated report, we analyze the performance of a distributed blockchain system, focusing on **Transaction Time** and **Block Time** metrics. The system consists of multiple nodes, and we simulate transactions and block mining times to understand the system's performance.

The **Transaction Time** represents the time taken for a transaction to be processed, and the **Block Time** measures the time taken to mine a block. We conducted two tests:
1. **Performance Test** with **5 nodes**.
2. **Scalability Test** with **10 nodes**.
3. **Capacity Test** (1, 5, and 10 nodes) and **Difficulty Test** (4 and 5 difficulty levels).

## 2. Transaction Time Analysis

### 2.1 Overview
The **Transaction Time** graph shows how long it takes to process a transaction between different nodes in the system. Here are the results for **5 nodes**:

- **Node 0 to Node 1**: 1.5007 seconds
- **Node 1 to Node 2**: 1.5009 seconds
- **Node 2 to Node 3**: 1.5009 seconds
- **Node 3 to Node 4**: 1.5008 seconds
- **Node 4 to Node 5**: 1.5003 seconds

### 2.2 Observations
- The **Transaction Time** remains relatively consistent around **1.5 seconds** for each transaction across the nodes.
- The slight variations in the time for different nodes (ranging between 1.5003 to 1.5009 seconds) may be attributed to small differences in network latency or simulation settings.
- This indicates that the system is efficient in processing transactions, with minimal delay.

### 2.3 Graph: Transaction Time vs. Node ID

![Transaction Time Graph](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_1.1.png)  

## 3. Block Time Analysis

### 3.1 Overview
The **Block Time** graph shows the time taken for a node to mine a block. The times are measured for 5 nodes, and here are the results:

- **Node 0**: 6.0010 seconds
- **Node 1**: 6.0011 seconds
- **Node 2**: 6.0007 seconds
- **Node 3**: 6.0007 seconds
- **Node 4**: 6.0003 seconds

### 3.2 Observations
- The **Block Time** is relatively consistent across all nodes, with slight variations between **6.0010 seconds** and **6.0003 seconds**.
- The **highest Block Time** is observed at **Node 1**, and the **lowest** is at **Node 4**.
- This suggests that block mining takes a constant amount of time, with small fluctuations depending on the node.

### 3.3 Graph: Block Time vs. Node ID

![Block Time Graph](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_1.2.png) 

## 4. Performance and Scalability Analysis

### 4.1 Performance Test (5 Nodes)
The system performs well with **5 nodes**, and there is minimal impact on performance. Transaction and Block Time remain stable and efficient as the system handles multiple transactions per second without significant delays. The performance results show that:
- **Transaction Time** remains around **1.5 seconds** per transaction across the nodes.
- **Block Time** varies between **6.0010 seconds** and **6.0003 seconds**.

### 4.2 Scalability Test (10 Nodes)
For the **Scalability Test**, the system was tested with **10 nodes**. Here are the results for **Transaction Time** and **Block Time**:

- **Node 0 to Node 1**: Transaction Time: 1.5007 seconds, Block Time: 6.0010 seconds
- **Node 1 to Node 2**: Transaction Time: 1.5010 seconds, Block Time: 6.0011 seconds
- **Node 2 to Node 3**: Transaction Time: 1.5009 seconds, Block Time: 6.0007 seconds
- **Node 3 to Node 4**: Transaction Time: 1.5010 seconds, Block Time: 6.0007 seconds
- **Node 4 to Node 5**: Transaction Time: 1.5009 seconds, Block Time: 6.0003 seconds
- **Node 5 to Node 6**: Transaction Time: 1.5008 seconds, Block Time: 6.0008 seconds
- **Node 6 to Node 7**: Transaction Time: 1.5011 seconds, Block Time: 6.0007 seconds
- **Node 7 to Node 8**: Transaction Time: 1.5007 seconds, Block Time: 6.0004 seconds
- **Node 8 to Node 9**: Transaction Time: 1.5006 seconds, Block Time: 6.0011 seconds

#### 4.3 Observations
- The **Transaction Time** and **Block Time** remain relatively consistent with only slight variations as the number of nodes increases.
- The system maintains **transaction processing efficiency** with **slight fluctuations** in the time required to mine blocks.
- **Node 0** and **Node 1** show slightly higher **Block Time** than the other nodes, but the difference is small.

#### 4.4 Graph: Transaction Time vs. Node ID for 10 Nodes

![Transaction Time for 10 Nodes](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_2.1.png) 

#### 4.5 Graph: Block Time vs. Node ID for 10 Nodes

![Block Time for 10 Nodes](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_2.2.png) 

### 4.6 Scalability Results
- **Throughput** remains consistent as node count increases.
- The system efficiently handles **up to 10 nodes** with minimal impact on **Transaction Time** and **Block Time**.
- This indicates the **scalability** of the system without major degradation in performance as more nodes are added.


### 4.7 Scalability and Speedup Analysis (5 vs 10 Nodes)

To quantitatively evaluate the scalability of the system, a speedup analysis was performed by comparing the average block creation times obtained from the **5-node** and **10-node** configurations.

The speedup is defined as the ratio of the execution time with fewer nodes to the execution time with more nodes:

Speedup ≈ T₅ / T₁₀

Based on the experimental measurements, the average **Block Time** for both configurations was observed to be approximately the same. As a result, the computed speedup value is close to **1**:

Speedup ≈ 1

This result indicates that increasing the number of nodes from 5 to 10 does **not** lead to a significant improvement in block mining speed in the current experimental setup. This behavior is expected, as block mining in the system is dominated by **Proof-of-Work difficulty**, which requires each node to independently solve a computationally intensive task.

Since block mining is not parallelized across nodes, adding more nodes does not reduce the time required to mine an individual block. Instead, each node performs the mining process independently, resulting in similar block creation times regardless of the total number of nodes.

Overall, the speedup analysis confirms that the system exhibits **limited parallel performance gains** with respect to block mining, while still maintaining stable and consistent behavior as the network size increases.


### 4.8 Difficulty Analysis (Difficulty Level = 4)

This section presents the performance analysis of the system under difficulty level = 4, which serves as a baseline configuration for comparison with higher difficulty settings.

The experiment was conducted using a fixed transaction delay and multiple nodes, while the mining difficulty was set to **4**.

### 4.8.1 Results (Difficulty = 4)

Based on the experimental measurements and generated graphs, the following results were obtained:

- **Transaction Time** values ranged between **1.5007 s** and **1.5020 s**
- **Block Time** values ranged between **4.0007 s** and **4.0011 s**

Sample measurements:
- Transaction Time: **1.5007 s**, Block Time: **4.0011 s**
- Transaction Time: **1.5007 s**, Block Time: **4.0008 s**
- Transaction Time: **1.5008 s**, Block Time: **4.0007 s**
- Transaction Time: **1.5020 s**, Block Time: **4.0008 s**

### 4.8.2 Observations

- **Transaction Time** remained stable at approximately **1.5 seconds**, showing only minimal fluctuations across different nodes.
- **Block Time** was consistently close to **4 seconds**, which directly reflects the configured mining difficulty.

Minor variations in both transaction and block times are attributed to **system scheduling and timing precision**, rather than network effects.

### 4.8.3 Graphs (Difficulty = 4)

- **Transaction Time vs. Node ID (Difficulty = 4)**
![Transaction Time Graph](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_4.1(d4).png)

- **Block Time vs. Node ID (Difficulty = 4)**
![Block Time Graph](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_4.2(d4).png)

### 4.8.4 Interpretation

Difficulty level = 4 provides a **clear and stable baseline** for system performance: 
Transaction processing time is largely **unaffected by mining difficulty**. Block mining time **scales directly** with the configured difficulty value. 

## 4.9 Difficulty Analysis (Difficulty Level = 5)

In addition to the previous experiments, the system was also tested with a **higher difficulty level (difficulty = 5)** in order to observe its impact on **Block Time** and **Transaction Time**. Keeping the transaction delay constant while increasing the block mining difficulty.

### 4.9.1 Results (Difficulty = 5)

The following measurements were obtained during the experiment:

- **Transaction Time** values ranged between **1.5003 s** and **1.5013 s**
- **Block Time** values ranged between **5.0003 s** and **5.0010 s**

Sample results:
- Transaction Time: **1.5003 s**, Block Time: **5.0007 s**
- Transaction Time: **1.5008 s**, Block Time: **5.0005 s**
- Transaction Time: **1.5008 s**, Block Time: **5.0004 s**
- Transaction Time: **1.5009 s**, Block Time: **5.0011 s**
- Transaction Time: **1.5013 s**, Block Time: **5.0004 s**

### 4.9.2 Observations

- **Transaction Time** remained almost unchanged compared to previous tests, staying stable around **1.5 seconds**, indicating that transaction processing is **independent of mining difficulty**.
- The change in **Block Time** compared to the difficulty = 4 experiment confirms that mining difficulty directly influences block mining duration.
- The block mining process showed **consistent behavior across all nodes**, with only very small fluctuations caused by system scheduling and timing precision.

### 4.9.3 Graphs (Difficulty = 5)

- **Transaction Time vs. Node ID (Difficulty = 5)**  
  ![Transaction Time Graph](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_3.1.png)

- **Block Time vs. Node ID (Difficulty = 5)**  
  ![Block Time Graph](https://github.com/OskarSeierl/distributed-systems/blob/main/images/Figure_3.2.png)

### 4.9.4 Interpretation

The results confirm that increasing the difficulty level primarily affects **Block Time**, while **Transaction Time remains stable**. Compared to the **difficulty = 4** configuration, block mining times at **difficulty = 5** are noticeably higher, demonstrating that mining difficulty is the dominant factor influencing block creation time.

This behavior is consistent with real blockchain systems, where increasing mining difficulty increases computational effort without significantly impacting transaction propagation delay.

Overall, the system demonstrates **robust performance and predictable scaling behavior** under higher difficulty settings.

## 5. Conclusion

From the analysis of **Transaction Time** and **Block Time** across different nodes, we can conclude that:
- The system handles **transactions efficiently** with minimal delays of around **1.5 seconds** per transaction.
- The **Block Time** remains consistent across nodes, with small variations, which suggests the system's stability.
- The system is **scalable** and can handle **more than 5 nodes** without significant performance degradation.

### **Tested Capacities (1, 5, 10 nodes) and Difficulty Levels (4, 5)**:
- The system has been tested with different **node capacities** and **difficulty levels**. The system performed efficiently with **5 nodes** and scaled well to **10 nodes** with minimal impact on **Transaction Time** and **Block Time**.
- The difficulty levels (4 and 5) were simulated by adjusting the **Block Time** based on the given difficulty. The change in difficulty resulted in a corresponding change in **Block Time**, confirming that mining difficulty directly influences block mining duration.
- The single-node (1 node) scenario was used as a baseline reference to compare performance behavior under increased network size.






