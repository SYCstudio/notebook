# Chapter 2 A model of distributed computations

## A distributed program

A distributed program is composed of a set of n asynchronous processes $p_1, p_2, \dots , p_i, \dots , p_n$ that communicate by message passing over the communication network.  
There is no global memory, communication only by passing messages.  
Let $C_{ij}$ denotes the channel from process $p_i$ to process $p_j$ , and let $m_{ij}$ denotes the message.  
The communication delay is finite but unpredictable.  
Also, there is no shared global clock which can be accessible instantaneously.  
Process execution and message transfer are asynchronous.

The global state of a distributed computation is composed of the states of the processes and the communication channels.  
The state of the processes is characterized by the state of its local memory and depends upon the context.  
The state of a channel is characterized by the set of messages in transit in the channel.

## A model of distributed execution

The execution of a process consists of a sequential execution of its actions.  
Actions are atomic. They are modeled as three types of events: internal events, message send events, message receive events.  
Let $e^x_i$ denote the $xth$ event at process $p_i$. For message $m$, let $send(m)$ and $rec(m)$ denote its send and receive events.

The occurrence of events changes the states of respective processes and channels, thus causing transitions in the global system state.

* Internal event: change the state of the process.  
* Send event / Receive event: change the state of the process and the state of the channel.

The events at a process are linearly ordered by their order of occurrence.  
The execution of process pi produces a sequence of events $e^1_i, e^2_i, \dots, e^x_i, e^{x+1}_i, \dots$, and is denoted by $\mathcal{H}_i, \mathcal{H}_i = (h_i, \rightarrow_i)$ where $h_i$ is the set of events produced by $p_i$ and binary relation $\rightarrow_i$ defines a linear order on these events. Relation $\rightarrow_i$ expresses causal dependencies among the events of $p_i$. 

The send and receive events establish causal dependency from the sender process to the receive process.  
Relation $\rightarrow_{msg}$ capture this causal dependency: $send(m) \rightarrow_{msg} rec(m)$.

The evolution of a distributed execution is depicted by a *space–time diagram*.  Here is an example.

![[assets/计算机/Distributed-and-Concurrency-System/Distributed-Computing-Principles-Algorithms-and-Systems/chapter_2_A_model_of_distributed_computations-1786945024357.jpeg]]

### Causal precedence relation

Let $H = \cup_i h_i$ denote the set of events executed in a distributed computation.  
We define a binary relation on the set H, denoted as $\rightarrow$, expresses causal dependencies between events in the distributed execution.

$$
\forall e_i^x,\ \forall e_j^y \in H,\quad
e_i^x \rightarrow e_j^y
\iff
\left\{
\begin{aligned}
& e_i^x \rightarrow_i e_j^y
\quad \text{i.e., } (i=j)\land(x<y) \\
& \text{or} \\
& e_i^x \rightarrow_{\mathrm{msg}} e_j^y \\
& \text{or} \\
& \exists e_k^z \in H:
\ e_i^x \rightarrow e_k^z
\land
e_k^z \rightarrow e_j^y
\end{aligned}
\right.
$$

The causal precedence relation induces an irreflexive partial order on the events of a distributed computation that is denoted as $\mathcal{H} = (H, \rightarrow)$ .  
For any two events $e_i, e_j$, $e_i \not \rightarrow e_j \not\Rightarrow e_j \not\rightarrow e_i$, and $e_i \rightarrow e_j \Rightarrow e_j \not\rightarrow e_i$  .  
If $e_i \not\rightarrow e_j$ and $e_j \not\rightarrow e_i$ then events $e_i$ and $e_j$ are said to be concurrent, and the relation is denoted as $e_i \parallel e_j$. This relation is not transitive.   
For any two events, $e_i \rightarrow e_j$ or $e_j \rightarrow e_i$ or $e_i \parallel e_j$. 

### Logical vs. physical concurrency

Logical concurrency: the events do not causally affect each other.  
Physical concurrency: events occur at the same instant in physical time.

Whether a set of logically concurrent events coincide in the physical time or in what order in the physical time they occur does not change the outcome of the computation.  
Therefore, we can assume a set of logically concurrent events occur at the same instant in physical time, for practical and theoretical purposes.

## Models of communication networks

There are several models of the service provided by communication networks.

* FIFO: first-in, first-out message queue. Message ordering is preserved by a channel.  
* non-FIFO: the channel acts like a set. Both messages adding and removing in a random order.  
* Causal ordering: satisfy the following property: $CO$: For any two messages $m_{ij}$ and $m_{kj}$, if $send(m_{ij}) \rightarrow send(m_{kj})$, then $rec(m_{ij}) \rightarrow rec(m_{kj})$  

This property ensures that causally related messages destined to the same destination are delivered in an order that is consistent with their causality relation.  
Note that $CO \subset FIFO \subset Non-FIFO$ .  

Causal ordering model is useful in developing distributed algorithms.   
Generally, it considerably simplifies the design of distributed algorithms because it provides a built-in synchronization.

## Global state of a distributed system

The global state of a distributed system is a collection of the local states of its components: the processes and the communication channels.  
The occurrence of events changes the states of respective processes and channels, thus causing transitions in global system state.

Let $LS^x_i$ denote the state of process $p_i$ after the occurrence of event $e^x_i$ and before the event $e^{x+1}_i$. $LS^0_i$ denote the initial state of process $p_i$.  
Let $send(m) \le LS^x_i$ denote the fact that $\exists y, 1\le y\le x, e^y_i = send(m)$. Let $rec(m) \not\le LS^x_i$ denote the fact that $\forall y, 1\le y \le x, e^y_i \neq rec(m)$.

Let $SC^{x, y}_{ij}$ denote the state of a channel $C_{ij}$ defined as:

$$
SC_{ij}^{x,y}
=
\{m_{ij}\mid send(m_{ij}) \le LS_i^x \land rec(m_{ij}) \nleq LS_j^y\}
$$

Thus, channel state$SC^{x, y}_{ij}$  denotes all messages that $p_i$ sent up to event $e^x_i$ and  which process $p_j$ had not received until event $e^y_j$ .

### Global state

The global state is a collection of the local states of the processes and the channels. $GS = \{ \bigcup_i LS^{x_i}_i, \bigcup_{j,k}SC^{y_j, z_k}_{jk}\}$  .  
A meaningful global snapshot asks all the states to be recorded at the same instant. However, it is impossible since the clock can not be synchronized perfectly.  
Even if the state is not been recorded at the same instant, it can still be meaningful, as long as every message that is recorded as received is also recorded as sent.  
That is, the state should not violate the causality, a message cannot be received if it was not sent.  
We call these type of states *consistent global states* and they are meaningful global states.

A global state GS is a consistent global state iff it satisfies the following condition:

$$ \forall m_{ij}:\quad
send(m_{ij}) \nleq LS_i^{x_i}
\;\Rightarrow\;
m_{ij} \notin SC_{ij}^{x_i,y_j}
\land
rec(m_{ij}) \nleq LS_j^{y_j}.
$$

A global state GS is *transitless* iff 

$$
\forall i,j \in \{1,\dots,n\},\qquad
SC_{ij}^{y_i,z_j}=\varnothing.
$$
 A global state is *strongly consistent* iff it is transitless as well as consistent.

## Cuts of a distributed computation

In the space–time diagram of a distributed computation, a zigzag line joining one arbitrary point on each process line is termed a *cut* in the computation.  
The set of events are sliced into a $PAST$ and a $FUTURE$. For cut $C$, denote $PAST(C)$ and $FUTURE(C)$.  
Every cut corresponds to a global state, and every global state can be graphically represented as a cut in the computation’s space–time diagram.

> If $e_i^{\operatorname{Max\_PAST}_i(C)}$ denotes the latest event at process $p_i$ that is in the **PAST** of a cut $C$, then the global state represented by the cut is $\left\{\bigcup_i LS_i^{\operatorname{Max\_PAST}_i(C)},\;\bigcup_{j,k} SC_{jk}^{y_j,z_k}\right\}$ where $SC_{jk}^{y_j,z_k}=\left\{m\mid send(m)\in \operatorname{PAST}(C)\land rec(m)\in \operatorname{FUTURE}(C)\right\}.$ 

A consistent global state corresponds to a consistent cut, in which every message received in the $PAST$ of the cut was sent in the $PAST$ of that cut.

## Past and future cones of an event

In a distributed computation, an event $e_j$ could have been affected only by all events $e_i$ such that $e_i \rightarrow e_j$ and all the information available at $e_i$ could be made accessible at $e_j$.  
Let $Past(e_j)$ denote all events in the past of $e_j$ in a computation $(H, \rightarrow)$: $Past(e_j) = \{ e_i \mid \forall e_i \in H, e_i \rightarrow e_j\}$ .   
Let $Past_i(e_j)$ be the set of all those events of $Past(e_j)$ that are on process $p_i$.  
$Past_i(e_j)$ is a totally ordered set, by relation $\rightarrow_i$, whose maximal element is denoted by $max(Past_i(e_j))$.  It is always a message send event.  
Let $MaxPast(e_j)=\bigcup_{\forall i}\{ max(Past_i(e_j))\}$. It consists of the latest event at every process that affected event $e_j$ and is referred to as the *surface of the past cone* of $e_j$.  $MaxPast(e_j)$ is a consistent cut.  

We can define $Future(e_j)$, $Future_i(e_j)$, $MinFuture(e_j)$ similarly. 

All the events at process $p_i$ that occurred after $max(Past_i(e_j))$ but before $min(Future_i(e_j))$ are concurrent with $e_j$.

## Models of process communications

There are two basic models: synchronous and asynchronous.

* Synchronous communication: the sender blocks until the message has been received.  Simpler to handle but have poor performance and more prone to deadlock.
* Asynchronous communication: the sender does not wait for the message to be delivered. Higher parallelism but asks more complex buffer management.