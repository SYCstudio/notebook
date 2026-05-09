# TLT Towards Timeout-less Transport in Commodity Datacenter Networks
[EuroSys21]

## Goal
在数据中心网络中，使用现有的商业交换机已经提供的功能（即不需要开发新的交换机硬件设备），实现 timeoutless 网络。主要关注减少 short bursty flows 的 tail latency。

## Overview
key-idea：使用交换机上已有的染色方法，将包染成不同的颜色以区分 important 和 unimportant。  
交换机使用颜色信息决定丢包（important 的包除非最极端的情况不丢），端系统上的算法决定如何染色。

在交换机上：  
color aware dropping：使用 dynamic buffer allocation 技术在交换机上保证 important 包始终有 buffer 可用。这就意味着当出出现拥塞时可能丢弃不重要的包。  
如果交换机需要同时支持传统的流和 TLT 流，则需要将两者的队列完全分开，否则传统的流会占据 TLT 流的 important 包的空间，导致其算法失效。

在端系统上：  
分为 window-based 和 rate-based 两种来设计染色方法。中心思想：尽可能少地将包标记为重要的；控制包（SYN,FIN,RST）等小包全都标记为重要的。可以设计为挂载在不同的已有传输控制算法上  
window-based：ACK-clocking ，一个流在同一时间最多只会有一个重要的包在网络中。  
rate-based：将流的最后一个包标记为重要的，将重传的第一个包也标记为重要的。  

## Other
