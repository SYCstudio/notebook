# 深入浅出 DPDK

## 第二章 cache 与内存
### cache 预取
以 intel Netburst 架构为例
在这一架构中，每一级 cache 都有相应的预取机制，包括数据预取单元（基于流的预取单元，当程序以地址递增的方式访问数据时激活）和基于指令寄存器 IP 的预取单元（监测指令的读取，当发现读取数据块的大小固定时激活）。cache 预取还需要满足很多额外的条件才能激活。  
在 DPDK 中，控制结构体和数据缓冲区的都不遵循硬件预取原则，所以需要手动指定预取指令来加载相应数据。

### cache 一致性
首先是关于 cache 对齐，DPDK 中使用宏 `__rte_cache_aligned` 来保证结构体对齐，现代编译器也会尽量做到 cache line 对齐。   
更复杂的事 cache 一致性的要求。这一问题有几个前提：多核处理器，每个核独占 cache 和 cache 的策略为写回。关于这一问题的解决机制常用的有两种：基于目录的协议和总线窥探协议。  
在基于目录的协议中，由目录表统一管理所有的数据，处理器申请访问内存和修改内存都要向目录表提出申请。这一协议的延迟较大，但在有很多处理器的系统中扩展性很好。  
在基于总线的协议中，当某一处理器使用某缓存内容时，该处理器要负责监听总线，一方面在本地修改内容后要广播到其它处理器，另一方面当接收到其它处理器的广播后要更新本地备份的内容。一个经典的总线协议是 MESI 协议。总线协议要求系统具有广播能力，适合小规模的多核系统。  
DPDK 使用多种方式避免 cache 一致性问题。比如：将数据结构为每一个核单独定义一份，让每个核访问自己独占的数据结构备份；在处理网卡收发时，DPDK 会为每一个核维护单独的接收队列和发送队列，避免多个核对网卡的竞争。

### DDIO
传统的服务器处理数据的方式是：网卡通过外部总线（如 PCI 总线）把数据核报文描述符送到内存，再由 CPU 将内存数据加载进 cache，处理后再写回 cache，最送回内存，CPU 通知网卡从内存中拿数据，经由外部总线送到网卡缓存，最后通过网络接口发送出去。  
这一流程涉及到多次访问内存，而内存相对 CPU 是较慢的。DDIO 技术绕过内存，将网络报文直接存储在 LLC Cache 中，显著加速了这一过程。

## 第三章 并行计算
### 多核性能和可扩展性
#### 亲和性
在多核系统上，CPU 亲和性指的是让一个特定的任务尽可能长时间地在某个给定 CPU 上运行，且被迁移到其它处理器上的倾向尽量小。   
在 Linux 系统中，每一个线程都有一个相关的数据结构 `task_struct`，其中有一个 `cpus_allowed`位掩码与亲和性相关，这个位掩码由 n 位组成，与系统中的 n 个逻辑处理器一一对应，如果对某个特定的进程设置了指定的位，那么这些线程就可以在相关 CPU 上运行。Linux 内核提供了若干方法来让用户能够修改或查看当前位掩码。

> 为什么使用亲和性  
> 对于多核系统，最直接的好处是提高了 CPU Cache 的命中率。特别是在 NUMA 架构下，因为任何跨 NUMA 节点的任务切换都会导致大量三级 Cache 的丢失。  
> 另一个好处是减少 CPU 进行线程调度的压力。

DPDK 把线程绑定到逻辑核来避免跨核切换带来的开销。对于绑定逻辑核，仍然可能会出现线程切换的情况，可以将逻辑核从内核调度系统剥离。

#### DPDK 的多线程
DPDK 线程基于 pthread 接口创建，属于抢占式线程模型，受内核调度支配。  
DPDK 支持在多核设备上创建多个线程，然后绑定到单独的核上。  
