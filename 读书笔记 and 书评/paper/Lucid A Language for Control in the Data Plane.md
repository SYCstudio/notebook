# Lucid A Language for Control in the Data Plane
[SIGCOMM 2016]

## Introduction

Challenges

* Expressing control logic in packet processing abstractions (disjoint and low level primitive such as parser, match-action unit and packet recirculation)  
* Strict limitation of operating on persistent state (registers)  
* The data-plane language is hard to debug  

Lucid: Event and handler  

* Event: carries user-specific data  
* Handler: define the computation

correct-by-construction approach: domain-specific syntactic constraints, and a novel type system.

Packet-driven: break control tasks down into atomic operations driven by the arrival of packets

