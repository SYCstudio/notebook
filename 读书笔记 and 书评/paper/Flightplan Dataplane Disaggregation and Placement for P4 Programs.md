# Flightplan-Dataplane Disaggregation and Placement for P4 Programs
[NSDI 2021]

## Goal
将单一 p4 程序进行分解，部署到异构的计算设备上以实现更好的性能。

## Overview
key-idea：分析 p4 程序，将其分解成为若干子程序块，再依次输入网络中各计算设备的能力、要求和网络拓扑，根据此生成合理的划分方案并部署到实际机器上。

如何进行划分实际上是人工使用扩展的语言在 p4 代码中显示指定的（文章中虽然也提到了可以由程序自动生成，但并没有提到是何程序，也没有提到划分的算法，估计实际实现的时候仍然是提前做好划分的）。  
在划分之后，静态分析 p4 代码得到每个部分的资源占用和要求（这里要检查所有的程序路径），然后检查与硬件资源能力是否匹配。  
然后再是输入拓扑（结合后面的实验，这里的拓扑更像是把原本交换机上需要的计算过程 offload 到与交换机相连的计算设备上，后面也提到要为这个大 p4 程序配置一个中心交换机，其能使用的外围设备就是与该交换机相连的）。  
程序分解就涉及到分解之后不同部分之间的通信，文章给出了两种不同的模式（runtime），一种 full 的需要在包头增加中间信息（比如线性化之后的 metadata），该方法能够完成所有的任务；另一种 headerless 的则不需要新增自定义包头，但对于那些需要额外传递中间任务的划分方式无解。

## Other
前面说了一大堆，又是网络拓扑配置，又是各个计算设备的能力如何形式化，最后到 planner 的时候才发现，原来只是简单的将交换机的功能 offload 到与交换机直接相连的其它计算设备上，controller 其实负责的是如何将这些设备链接起来。交换机在这里发挥的类似一台大计算机中的类似南桥的功能，难怪最后也提到可以用普通商业交换机做到。
