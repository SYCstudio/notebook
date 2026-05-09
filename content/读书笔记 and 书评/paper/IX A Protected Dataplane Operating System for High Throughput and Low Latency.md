# IX A Protected Dataplane Operating System for High Throughput and Low Latency

[osdi]

## Abstract
hardware virtualization: seperate managing and scheduling functions of the kernel from network processing.

## Instruction
4-way tradeoff: high throughput, low latency, strong protection, and resource efficiency  
control plane - full Linux kernel.  
data plane - protected, library-based operating system on dedicated hardware thread.  
