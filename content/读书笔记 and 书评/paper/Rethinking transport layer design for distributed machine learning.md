# Rethinking transport layer design for distributed machine learning
[APNet19]

## Goal
基于 SGD 的分布式机器学习具有一些独特的数据特征。文章指出，机器学习算法是 bounded-loss tolenant 的，并进一步给出了与这一观察有关的实验和未来工作的想法。

## Overview
观察：今天的分布式机器学习很受 tail latency 影响，而一个流的完成时间很大程度上又是由丢包重传这一恢复机制导致的。  
像是 SGD 这样的机器学习算法本身就是 approximation algorithm，所以在每一轮同步时传输精确的结果并无必要。  
模拟实验结果说明，如果将完全不丢包的情形作为基准，对于随机的数据丢失的占比，存在两个数字节点 $(x_1, x_2)$ ：

* 当丢包占比 $p \le x_1$ 时，任务达到与基准相同的 converge 所需的 epoch 相同，且因为更少的 tail latency 影响，整个任务的完成时间也更短。  
* 当 $x_1 < p \le x_2$ 时，任务需要更多的 epoch 才能达到相同 converge。  
* 当 $p > x_2$ 时，任务无论增加多少 epoch 也无法达到相同的 converge，这意味着通信损失导致了应用的性能下降。

论文还通过模拟实验证明，无论是在应用层采取主动直接丢弃参数的方式，还是采用其他参数同步方案，或者使用现有的其他通信协议（比如 UDP）都是不能很好地解决这个问题的。

bounded-loss tolerant 协议处理丢包的方法：  

* 能够快速侦测到的丢包（如重复 ACK）和原本一样需要快速重传。  
* 在限制条件下（如允许的丢包率），允许长时间的丢包被直接丢弃。

上述协议的最大贡献是 cut the tail latency。

需要考虑的存在的问题：如何正确地翻译包（数据格式？设计包）
