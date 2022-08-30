# Fast and Light Bandwidth Testing for Internet Users

[NSDI 2021]

## Goal
fast, light, low data usage, small-scale test server, high accuracy

## Overview
key idea: accommodate and exploit the noise (rather than combat the noise)

### Fuzzy Rejection Sampling
P(x) - measured distribution , T(x) - target distribution (can't be known beforehand)  
narrows down P(x) as the boundary of T(x) to bootstrap T(x) modeling (Elastic Bandwidth Probing: tune the transport-layer data probing rate based on its deviation from the currently-estimated bandwidth)  

### Crucial Interval Sampling
crucial interval: the true samples tend to concentrate within a narrow throughput interval 
+ Datadriven Server Selection (DSS) and Adaptive Multi-Homing (AMH) mechanisms

searches for a dense and narrow interval that covers the majority of the desirable samples

### Elastic Bandwidth Probing
from BBR  
generate throughput sample that obey the distribution of the target bandwidth  

### Data-driven Server Selection
select the server with the highest bandwidth estimation  
model data from past test (rtt, bandwidth)

### Adaptive Multi-Homing
multiple parallel connection with different testing server 
important when the last mile of access link is not the bottleneck

## Extension

## Others

### Aceeptance-rejection Sampling （接收-拒绝采样）
一种采样策略。对于需要测定的概率分布 $p(z)=\frac 1 {Z_p}\overline{p}(z)$，其中 $Z_p$ 为未知的归一化常数，$\overline{p}(z)$ 已知。借助一个已知的简单参考分布 $q(z)$，并引入常数 $k$ 使得 $kq(z) \ge \overline{p}(z)$ 始终成立。在每次采样时，首先根据 $q(z)$ 采样得到一个 $z_0$，然后在区间 $[0, kq(z_0)]$ 均匀采样得到 $u_0$，若 $u_0 \le \overline{p}(z_0)$，则接收，否则拒绝。最后得到的数据就是对 $p(z)$ 的近似估计。