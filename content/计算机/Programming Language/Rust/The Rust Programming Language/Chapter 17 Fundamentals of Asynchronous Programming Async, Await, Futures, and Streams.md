# Chapter 17 Fundamentals of Asynchronous Programming: Async, Await, Futures, and Streams


## Parallelism and Concurrency 

Here is a concurrent workflow.

![[assets/计算机/Programming-Language/Rust/The-Rust-Programming-Language/Chapter_17_Fundamentals_of_Asynchronous_Programming_Async,_Await,_Futures,_and_Streams-1785573624860.jpeg]]

Hers is a parallel workflow.

![[assets/计算机/Programming-Language/Rust/The-Rust-Programming-Language/Chapter_17_Fundamentals_of_Asynchronous_Programming_Async,_Await,_Futures,_and_Streams-1785573783583.jpeg]]

Running async code in Rust usually happens concurrently. Depending on the hardware, the operating system, and the async runtime we are using (more on async runtimes shortly), that concurrency may also use parallelism under the hood.

## Futures and the Async Syntax

`Future`: a value that may not be ready now, but will become ready at some point in the future.   
Rust provides a `Future` trait.  
`async` keyword is applied to blocks and functions to specify that they can be interrupted and resumed.  
We use `await` keyword in an async block or function to await a future (wait for it to become ready).  
Any point where you await a future within an async block or function is a potential spot for that block or function to pause and resume.   
The process of checking with a future to see if its value is available yet is called *polling*.

When Rust sees a block marked with the `async` keyword, it compiles it into a unique, anonymous data type that implements the `Future` trait. When Rust sees a function marked with `async`, it compiles it into a non-async function whose body is an async block. An async function’s return type is the anonymous data type the compiler creates for that async block.

In Rust, the `main` function can't be marked `async` since it is the entry of the program.  
Async code needs a *runtime* that manages the details of executing asynchronous code. There are many different async runtimes available, for different scenario.

Rust's futures are lazy. Without a `await`, it will do nothing.

## Applying Concurrency with Async

The API for working with concurrency using async may be similar to those for using threads. However, they often have different behavior and performance characteristics.  

### Creating a New Task with `spawn_task`

Here is an example that use a similar form of `spawn` and `sleep`.

```rust
extern crate trpl; // required for mdbook test

use std::time::Duration;

fn main() {
    trpl::block_on(async {
        let handle = trpl::spawn_task(async {
            for i in 1..10 {
                println!("hi number {i} from the first task!");
                trpl::sleep(Duration::from_millis(500)).await;
            }
        });

        for i in 1..5 {
            println!("hi number {i} from the second task!");
            trpl::sleep(Duration::from_millis(500)).await;
        }

        handle.await.unwrap();
    });
}
```

The bigger difference is that we didn't need to spawn another operating system thread.

We can use `join` method to complete multiple futures. It produces a single new future whose output is a tuple containing the output of each input future in once they both complete.

```rust
        let fut1 = async {
            for i in 1..10 {
                println!("hi number {i} from the first task!");
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        let fut2 = async {
            for i in 1..5 {
                println!("hi number {i} from the second task!");
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        trpl::join(fut1, fut2).await;
```

Note that the above program output exact same order every time. This is because the `trpl::join` function is fair: it checks each function equally often, alternating between them, and never lets one race ahead if the other is ready.  
Runtimes don’t have to guarantee fairness for any given operation, and they often offer different APIs to let you choose whether you want fairness.

### Sending Data Between Two Tasks

We can use message passing to share data between futures. Here is an example

```rust
        let (tx, mut rx) = trpl::channel();

        let val = String::from("hi");
        tx.send(val).unwrap();

        let received = rx.recv().await.unwrap();
        println!("received '{received}'");

```

Unlike the synchronous `Receiver::recv`, which blocks until it receives a message, the `trpl::Receiver::recv` hands control back to the runtime until either a message is received or the send side of the channel closes. We don't await the `send` call.

The following example sends multiple message via the `trpl::channel`.

```rust
extern crate trpl; // required for mdbook test

use std::time::Duration;

fn main() {
    trpl::block_on(async {
        let (tx, mut rx) = trpl::channel();

        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("future"),
        ];

        for val in vals {
            tx.send(val).unwrap();
            trpl::sleep(Duration::from_millis(500)).await;
        }

        while let Some(value) = rx.recv().await {
            println!("received '{value}'");
        }
    });
}
```

The program can compile and run successfully. However, the messages do not arrive at half-second intervals as expected. They arrive all at once, two seconds after we start the program. For another, it also never exits.  
For the first problem, the order in which `await` keywords appear in the code is also the order in which they are executed, within a given async block. So the program above will run linearly. There's still no concurrency.  
By putting the `tx` and `rx` operations in their own async blocks, we can get the expected behavior.

```rust
        let tx_fut = async {
            let vals = vec![
                String::from("hi"),
                String::from("from"),
                String::from("the"),
                String::from("future"),
            ];

            for val in vals {
                tx.send(val).unwrap();
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        let rx_fut = async {
            while let Some(value) = rx.recv().await {
                println!("received '{value}'");
            }
        };

        trpl::join(tx_fut, rx_fut).await;
```

However, the program still not exit.  
The second problem is about the ownership. The async block where we send the messages only *borrows* `tx`. So the `tx` will never be dropped.  
If we could *move* tx into that async block, it would be dropped once that block ends. Changing the `let tx_fut = async {` to `let tx_fut = async move {` can solve the problem.

This channel also support multiple sender. Just like the threads' version of `channel`, we can use `clone()` and transfer it to multiple closure.

### Yielding Control to the Runtime

Rust only pauses async blocks and hands control back to a runtime at an await point. Everything between await points is synchronous.  
This may results in *starving* if the block is big.  
We can use yield `trpl::yield_now().await` to let operations switch off making progress.  
This is a form of *cooperative multitasking*, where each future has the power to determine when it hands over control via await points.  
Note that `yield` is relatively inexpensive in some cases, but it is not free.

## Streams: Futures in Sequence

A stream is like an asynchronous form of iteration.  
We can convert the iteration to steam. Here is an example.

```rust
extern crate trpl; // required for mdbook test

use trpl::StreamExt;

fn main() {
    trpl::block_on(async {
        let values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        // --snip--
        let iter = values.iter().map(|n| n * 2);
        let mut stream = trpl::stream_from_iter(iter);

        while let Some(value) = stream.next().await {
            println!("The value was: {value}");
        }
    });
}
```

## Futures, Tasks, and Threads

In many cases, the choice isn't threads or async but rather threads and async.  
When thinking about which method to use, consider these rules of thumb

1. If the work is very parallelizable (that is, CPU bound), such as processing  a bunch of data where each part can be processed separately, threads are a better choice.  
2. If the work is very concurrent (that is, I/O bound), such as handling messages from a bunch of different sources that may come in at different intervals or different rates, async is a better choice.

