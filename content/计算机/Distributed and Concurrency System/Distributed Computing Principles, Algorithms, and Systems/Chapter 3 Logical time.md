# Chapter 3 Logical time

## Introduction

In distributed systems, it is not possible to have global physical time.  
The logical time is sufficient to capture the fundamental monotonicity property associated with causality in distributed systems.

There are three ways to implement logical time: scalar time, vector time, and matrix time.

In a system of logical clocks, every process has a logical clock that is advanced using a set of rules.  
Every event is assigned a timestamp and the causality relation between events can be generally inferred from their timestamps.

## A framework for a system of logical clocks

### Definition

A system of logical clocks consists of a time domain $T$ and a logical clock $C$.   
Elements of $T$ form a partially ordered set over a relation $<$, which is usually called the *happened before* or *causal precedence*.  
The logical clock $C$ maps an event $e$ to an element in the time domain $T$, denoted as $C(e)$ and called the timestamp of $e$. $C : H \mapsto T$ , which satisfied the property $\forall e_i \rightarrow e_j, C(e_i) < C(e_j)$.  
This monotonicity property is called the *clock consistency condition*.  
When $e_i \rightarrow e_j \Leftrightarrow C(e_i) < C(e_j)$, the system of clocks is said to be *strongly consistent*.

### Implementing logical clocks

Implementation of logical clocks requires addressing two issues:

1. data structures local to every process to represent logical time  
2. a protocol (set of rules) to update the data structures to ensure the consistency condition

Each process $p_i$ maintains data structures that allow it the following two capabilities

* A local logical clock, denoted by $lc_i$, that helps process $p_i$ measure its own progress.  
* A logical global clock, denoted by $gc_i$, that is a representation of process $p_i$’s local view of the logical global time. It allows this process to assign consistent timestamps to its local events. Typically, $lc_i$ is a part of $gc_i$.

The protocol ensures a process's logical clock and its view of global time is managed consistently.  
The protocol consists of the following two rules:

1. R1: This rule governs how the local logical clock is updated by a process when it executes an event (send, receive, or internal).  
2. R2: This rule governs how a process updates its global logical clock to  update its view of the global time and global progress.  

## Scalar time

### Definition

The time domain in this representation is the set of non-negative integers.  
The logical local clock of process $p_i$ and its local view of the global time are squashed into one integer variable $C_i$.  

1. R1: Before execution an event, process $p_i$ execute $C_i := C_i + d (d > 0)$.  
2. R2: Each message piggybacks the clock value of its sender. At receiver side, the process $p_i$ receives a message with timestamp $C_{msg}$ execute:1.  $C_i := \max(C_i, C_{msg})$ ; 2. execute R1; 3. deliver the message.

### Basic properties

**Consistency property**: Scalar clocks satisfy the monotonicity and hence the consistency property. $e_i \rightarrow e_j \Rightarrow C(e_i) < C(e_j)$.

**Total ordering**: Scalar clocks can be used to totally order events. Let $(t, i)$ where $t$ is an event's time of occurrence and $i$ is the identity of the process. We can define the total order relation $\prec$ on x and y with timestamp $(h, i)$ and $(k, j)$ as $x \prec y \Leftrightarrow (h < k or (h = k and i < j))$.    
Since events that occur at the same logical scalar time are independent, they can be ordered using any arbitrary criterion without violating the causality relation $\rightarrow$.

**Event counting**: If we fix the increment value $d$ to $1$, we have the following properties: if event $e$ have a timestamp $h$, then $h-1$ represents the minimum logical duration, counted in units of events, required before producing the event $e$.

**No strong consistency**: $C(e_i) < C(e_j) \not\Rightarrow e_i \rightarrow e_j$. The reason that scalar clocks are not strongly consistent is that the logical local clock and logical global clock of a process are squashed into one, resulting in the loss causal dependency information among events at different processes.

## Vector time

### Definition

The time domain is represented by a set of n-dimensional non-negative integer vectors.  
Each process $p_i$ maintains a vector $vt_i[1..n]$ constitutes $p_i$'s view of the global logical time, where $vt_i[i]$ is the local logical clock, $vt_i[j]$ represents process $p_i$'s latest knowledge of process $p_j$'s local time.

* R1: Before executing an event, $vt_i[i] := vt_i[i] + d(d < 0)$.  
* R2: Each message $m$ is piggybacked with the vector clock $vt$. On the receipt of such a message $(m, vt)$, execute: 1. update its global logical time $vt_i[k] := \max(vt_i[k], vt[k])$; 2. execute R1; 3. deliver the message $m$.

Here is an example.

![[assets/计算机/Distributed-and-Concurrency-System/Distributed-Computing-Principles-Algorithms-and-Systems/Chapter_3_Logical_time-1787036627895.jpeg]]

We use the following rules to compare two vector timestamp: 

$$
\begin{aligned}
vh = vk
&\iff
\forall x:\ vh[x] = vk[x] \\

vh \le vk
&\iff
\forall x:\ vh[x] \le vk[x] \\

vh < vk
&\iff
vh \le vk
\land
\exists x:\ vh[x] < vk[x] \\
vh \parallel vk
&\iff
\neg(vh < vk)
\land
\neg(vk < vh)
\end{aligned}
$$

### Basic properties

**Isomorphism**: for two events $x$ and $y$, with timestamp $vh$ and $vk$, we have

$$
\begin{aligned}
x \rightarrow y &\iff vh < vk  \\
x \parallel y &\iff vh \parallel vk
\end{aligned}
$$

If events $x$ and $y$ respectively occurred at process $p_i$ and $p_j$ and are assigned timestamps $vh$ and $vk$, then

$$
\begin{aligned}
x \rightarrow y &\iff vh[i] \le vk[i] \\
x \parallel y &\iff vh[i] > vk[i] \land vh[j] < vk[j]
\end{aligned}
$$

**Strong consistency**: We can determine if the events are causally related by examining the vector timestamp of two events. The dimension of vector blocks cannot be less than $n$.  

**Event counting**: Fix $d$ to $1$, then the $ith$ component of vector clock at process $p_i$, the $vt_i[i]$, denotes the number of events that have occurred at $p_i$ until that instant.

### On the size of vector clocks


To explicitly track the progress at every other process, a vector clock of size $n$ is necessary.  
To determine the causality between a pair of events, a size equal to the dimension of the partial order $(E, \prec)$ is necessary, where the upper bound on this dimension is $n$.

> Dimension of the partial order.  
> Roughly, this property measure the complexity of partial order. It comes from the fact that, when we project a partial order into linear order, we will incorrectly define non-existing relation in the partial order. To exact describe the partial order, we need multiple linear order $L1, L2, \dots$ . By taking the intersection of such linear order, we can re-construct the original partial order.  
> The dimension of the partial order is defined as the minimum number of such linear extensions whose intersection gives exactly the partial order.

### Efficient implementations of vector clocks

The piggybacked message overhead grows linearly with the number of processors.  
We need technique to implement it efficiently.

**Differential technique**: Between successive message sends to the same process, only a few entries of the vector clock at the sender process are likely to change. So we can only send the differential. When a process $p_i$ sends message to a process $p_j$, it piggybacks only those entries of its vector clock that differ since the last message sent to $p_j$.

Straightforwardly implement the algorithm will take $O(n^2)$ space. We can maintain it into $O(n)$ space. Here is the algorithm.

Process $p_i$ maintains the following two additional vectors

* $LS_i[1..n]$ Last Sent: $LS_i[j]$ indicates the value of $vt_i[i]$ when process $p_i$ last sent a message to process $p_j$.  
* $LU_i[1..n]$ Last Update: $LU_i[j]$ indicates the value of $vt_i[i]$ when process $p_i$ last updated the entry $vt_i[j]$.

When $p_i$ sends a message to $p_j$, it sends only a set of tuples $\{(x, vt_i[x]) | LS_i[j] < LU_i[x]\}$.

**Direct-dependency technique**: Do not maintain vector clocks on-the-fly, only transmit a scalar value in the message. A process only maintains information regarding direct dependencies on other processes. The vector time for an event is constructed off-line from a recursive search of the direct dependency information at process.  

Each process $p_i$ maintains a dependency vector $D_i$, initialize with 0. $D_i$ is updated as follows:

1. Whenever an event occurs at $p_i$, $D_i[i] := D_i[i] + 1$.  
2. When $p_i$ sends a message to $p_j$, it piggybacks $D_i[i]$.  
3. When $p_i$ receives a message from $p_j$ with value $d$, $p_i$ updates $D_i[j] := \max(D_i[j], d)$.

In this rules, $D_i$ reflects only direct  dependencies. $D_i[j]$ denotes the sequence number of the latest event on process $p_j$ that *directly* affects the current state.  
The transitive dependencies are only can be obtained by recursively tracing the direct-dependency vectors of the events off-line.  
We can re-construct by calculating the latest dependent events on each process for a event, by updating and deducing the timestamp.
This technique is not suitable for application that require on-the-fly computation of vector timestamps.

**Jard–Jourdan’s adaptive technique**: In the direct-dependency technique, a process must observe an event after receiving a message but before sending out any message. If events occur very frequently, this technique will require recording the history of a large number of events.  
The Jard-Jourdan's technique comes from an idea that, when an observed event $e$ records its dependencies, then events that follow can determine their transitive dependencies. In that case, we can avoid the problem of recording a large amount of history.  
This technique define a *pseudo-direct* relation $\ll$ . If events $e_i$ and $e_j$ happen at process $p_i$ and $p_j$, the $e_i \ll e_j$ iff there exists a path of message transfer from $e_i$ to $e_j$, and there is no observed event on the path.  
The partial vector clock $p.vt_i$ at process $p_i$ is a list of tuples of the form $(j, v)$, indicating that the current state of $p_i$ is pseudo-dependent on the event on process $p_j$ whose sequence number is $v$. Initially, $p.vt_i=\{(i, 0)\}$ .  
Let $p.vt_i=\{(i_1, v_1), \dots, (i_n, v_n)\}$ , let $e.vt_i$ be a variable that holds the timestamp of the observed event.

1. When an event is observed at process $p_i$, the $p.vt_i$ are transferred to $e.vt_i$. $p.vt_i$ is reset. $e.vt_i := p.vt_i, p.vt_i := \{(i, v+1)\}$. 
2. When process $p_j$ sends a message to $p_i$, it piggybacks the $p.vt_j$ in the message.  
3. When $p_i$ receives a message with $p.vt$, $p_i$ updates $p.vt_i$ as the union of the $p.vt$ and $p.vt_i$. The same keys will update to max value.

## Matrix time

### Definition

The time is represented by a set of $n \times n$ matrices of non-negative integers.

* $mt_i[i, i]$ denotes the local logical clock of $p_i$.  
* $mt_i[i, j]$ denotes the latest knowledge that process $p_i$ has about the local logical clock, $mt_j[j, j]$, of process $p_j$  
* $mt_i[j, j]$ denotes the knowledge that process $p_i$ has about the latest knowledge that $p_j$ has about the local logical clock, $mt_k[k, k]$, of $p_k$.

The updating rules are:

* R1: Before executing an event, $mt_i[i][i] := mt_i[i][i] + d(d > 0)$  
* R2: Each message $m$ is piggybacked with matrix time $mt$. When $p_i$ receives a message $(m, mt)$ from a process $p_j$, it updates its global logical time: $1 \le k \le n: mt_i[i][k] := \max(mt_i[i][k], mt[j][k]); 1 \le k, l \le n: mt_i[k][l] := \max(mt_i[k][l], mt[k][l]);$, then execute R1 and deliver the message $m$.

### Basic properties

The vector $mt_i[i,.]$ contains all the properties of vector clocks.  
In addition, $\min_k(mt_i[k, l]) \ge t \Rightarrow$ process $p_i$ knows that every other process $p_j$ knows that $p_l$'s local time has progressed till $t$. So that all other processes know that $p_i$ will never send information with a local time $\le t$.

## Virtual time

Key design: time wrap mechanism. Processes execute with regard to other processes having synchronization conflict. When a conflict is discovered, the offending processes are rolled back to the time just before the conflict and executed forward along the revised path.

### Virtual time definition

Virtual time is a global, one-dimensional, temporal coordinate system.  
Virtual times are real values that are totally ordered by the less than relation $<$. It is implemented as a collection of several loosely synchronized local virtual clocks.

Processes communicate with each other by exchanging message, which contains: name of the sender and receiver, virtual send time and receive time.   
The virtual send time is the virtual time at the sender when the message is sent, whereas virtual receive time specifies the virtual time when the message must be received by the receiver.

It follows the tow semantic rules:

1. Virtual send time of each message $<$ virtual receive time of that message.  
2. Virtual time of each event in a process $<$ virtual time of next event in that process


### Comparison with Lamport's logical clocks

Lamport's logical clocks is partial order. It can be extended to total order by labeling each event with unique labels from the processes.  
Time warp mechanism is an inverse. It assumes that every event is labeled with a clock value from a totally ordered virtual time scale satisfying Lamport's clock conditions.

Lamport's clocks are conservatively maintained that they never violate causality.  
In virtual time, clocks are optimistically advanced. When a violation is detected, it takes corrective actions.

### Time warp mechanism

The message's timestamp is its virtual receive time. Each process must handle incoming messages in *timestamp* order.  
However, some processes may get ahead in virtual time of other process. So it is possible when a message with an earlier timestamp will arrive later. We need the time warp mechanism to solve this problem.

The time warp mechanism doesn't depend on the underlying computer architecture.  
The message may not be delivered in FIFO order.

There are two major parts: local control mechanism and global control mechanism.

#### The local control mechanism

Each process has a *local virtual clock* variable. There is no global virtual clock.  
The virtual clock changes only between events, not change during an event.  
All arriving messages at a process are stored in an input queue in increasing order of timestamp.  
When process next message from the input queue, the process will increases its local virtual clock to the timestamp of the message.  
When process send message, the virtual send time is copied from the sender's virtual clock.

Ideally, the message in the queue will in increasing order. However, due to the different computation rates, the message may be in disorder.  
When receiving a late message, the receiver rolls back to an earlier virtual time, cancelling all intermediate side effects and then executes forward again in the proper sequence.

Rollback in a distributed system is complicated by the fact that the process that wants to rollback might have sent many messages to other processes, which in turn might have sent many messages to other processes, and so on, leading to deep side effects.  
So messages must be effectively unsent and their side effects should be undone.  
This is achieved efficiently by using *antimessages*.

**Antimessages and the rollback mechanism**: For every message, there exists an antimessage that is the same in content but opposite in sign. Whenever a process sends a message, a copy of the message is transmitted to the receiver’s input queue and a negative copy (antimessage) is retained in the sender’s output queue for use in sender rollback.  
Whenever a message and its antimessage appear in the same queue, regardless of the order in which they arrived, they immediately annihilate each other resulting in shortening of the queue by one message.  
When receive a earlier message, the receiver need to rollback to a time earlier than the received message's timestamp. Then it sends the antimessages between the current state and earlier state. This will cause: 1. the antimessage will annihilate the message in the receiver's queue or 2. trigger the receiver rollback.

#### Global control mechanism

**Global virtual time (GVT)**: It is a property of an instantaneous global snapshot of system at real time *r*. It is the minimum of 1. all virtual times in all virtual clocks at time *r* and 2. the virtual send time of all messages that have been sent but have not yet been processed at time *r*.  
The GVT never decrease even though there may be roll back.  
Thus GVT can be viewed as a moving commitment horizon: any event with virtual time less than GVT cannot be rolled back and may be committed safely.

It is not possible to get the real GVT at any time *r*. But we can estimate it with $O(d)$ time, where *d* is the delay required for one broadcast to all processors in the system.  
The algorithm runs concurrently with the main computation and returns a value that is between the true GVT at the moment the algorithm starts and the true GVT at the moment of completion.   
Thus it gives a slightly out-of-date value for GVT which is the best one can get.

Time warp will periodically estimate GVT during execution. A higher frequency produces a faster response time and better space utilization but more processor time and network bandwidth.

**Application of GVT**

* Memory management and flow control: Information older than GVT is destroyed to avoid memory overheads.  
* Normal termination detection: When GVT reaches `+inf`, all the processes will terminate.  
* Error handling  
* Snapshots and crash recovery: An entire snapshot of the system at virtual time *t* can be constructed by a procedure in which each process “snapshots” itself as it passes virtual time t in the forward direction and “unsnapshots” itself whenever it rolls back over virtual time *t*.

## Physical clock synchronization: NTP

### Definitions and terminology

$C_a$ and $C_b$ are any two clocks.

* **Time**: The time of clock in a machine $p$ is given by function $C_p(t)$, where $C_p(t)=t$ for a perfect clock.  
* **Frequency**: Frequency is the rate at which a clock progresses. The frequency at time $t$ of clock $C_a$ is $C'_a(t)$ .  
* **Offset**: Clock offset is the difference between the time reported by a clock and the *real time*. $C_a(t)-t$. The offset of clock $C_a$ relative to $C_b$ is $C_a(t)-C_b(t)$.  
* **Skew**: The skew of a clock is the difference in the frequencies of the clock and the perfect clock. The skew of a clock $C_a$ relative to $C_b$ at time $t$ is $C'_a(t)-C'_b(t)$.  
* If the skew is bounded by $\rho$, clock values are allowed to diverge at a rate in the rate of $1-\rho$ to $1+\rho$.  
* **Drift**: The drift of clock $C_a$ is the second derivative of the clock value with respect to time $C''_a(t)$ .


### Clock inaccuracies

A clock is said to be working within $1-\rho \le \frac{dC}{dt} \le 1+\rho$ where constant $p$ is the maximum skew rate specified by the manufacturer.

The Network Timer Protocol (NTP) uses the *offset delay estimation* method.  
It involves a hierarchical tree of time server. The primary server at the root synchronizes with the UTC. The next level contains secondary severs, which is backup. At the lowest level has the clients.

![[assets/计算机/Distributed-and-Concurrency-System/Distributed-Computing-Principles-Algorithms-and-Systems/Chapter_3_Logical_time-1787649762321.jpeg]]

Let $a=T_1-T_3$ and $b=T_4-T_2$. We assume the network delay difference from $A$ to $B$ and from $B$ to $A$ is small. The clock offset $\theta$ and roundtrip delay $\delta$ of $B$ relative to $A$ at $T_4$ are approximately given by $\theta=\frac{a+b}{2}, \delta=a-b$.  
Each NTP message includes the latest three timestamps $T1, T2, T3$, while $T_4$ is determined upon arrival.

Here is the NTP protocol.

![[assets/计算机/Distributed-and-Concurrency-System/Distributed-Computing-Principles-Algorithms-and-Systems/Chapter_3_Logical_time-1787650026335.jpeg]]
