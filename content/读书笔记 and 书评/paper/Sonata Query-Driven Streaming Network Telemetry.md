# Sonata Query-Driven Streaming Network Telemetry
[SIGCOMM 2018]

## Goal
传统的网络测量方法（指在通用 CPU 和端系统上处理）不能很好地扩展到更大规模的集群上，Sonata 提出了将 stream processor 和 programmable switch 相结合的办法，将尽可能多的信息在交换机上处理，以此来提高处理速度。Sonata 设计了一套编译系统和原语，使开发人员能够更为简单地实现相关功能且不需要关注后端实际硬件，由编译系统自动划分和编译任务到交换机和边系统上。

## Overview
key idea：programmable switch 和 stream processor 拥有一个类似的处理模型（DAG），在硬件资源的约束条件下，通过合理的任务划分，将尽可能多的任务分派到交换机上执行，将交换机的高执行速率和边系统的通用处理能力结合起来。

Sonata 设计了一套通用的查询接口，允许配置员灵活地编写测量程序，且不需要考虑具体运行在哪一硬件上。其局限是，只支持 packet-level 的测量粒度（比如不支持那些需要重组 byte stream 的查询），且仅支持配置单台交换机（不支持跨越多个交换机的查询）。

量化可编程交换机的硬件限制，使用 Integer Linear Program 求解划分方案，目标是使尽可能少的包转发到 stream processor 上，即尽可能在 switch 上就处理完毕。使用历史采集到的流信息来确定在交换机上使用的资源。

为了减少发送到 stream processor 的包数量，同时减轻 switch 上开销，Sonata 使用 dynamic query refinement 技术将查询请求扩展为多个不同采集精度的查询。这一技术会对整个流程引入额外的延迟。

## Other
文章里并没有提到具体是如何使用 trace 做任务划分的，在 refinement 的时候也没有说明结果的精度和误差保证。
