# Chapter 16 Fearless Concurrency

The concepts of *ownership* and *type checking* in Rust making many concurrency errors are compile-time errors.  
As a lower-level language, Rust is expected to provide high performance solution and have fewer abstractions over the hardware.

## Using Threads to Run Code Simultaneously

An executed program runs in a process. Within the program, independent parts run in threads.  
Rust standard library use a *1:1* model of thread implementation, whereby a program uses one operating system thread per one language thread.

We call the `thread::spawn` and pass it a closure to create a new thread. Here is an example

```rust
use std::thread;
use std::time::Duration;

fn main() {
    thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {i} from the spawned thread!");
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {i} from the main thread!");
        thread::sleep(Duration::from_millis(1));
    }
}
```

Note that when the main thread of a Rust program completes, all spawned threads are shut down, whether or not they have finished running.  
We can fix the problem by saving the return value of `thread::spawn` in a variable, whose type is `JoinHandle<T>`.  
It is an owned value that, when we call the `join` method on it, will wait for its thread to finish. Here is the modification of the above example that make sure the thread can finish running.

```rust
use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {i} from the spawned thread!");
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {i} from the main thread!");
        thread::sleep(Duration::from_millis(1));
    }

    handle.join().unwrap();
}
```

### Using `move` Closures with Threads

We often use the `move` keyword to let the closure take ownership of the values.   
Thus, we can transfer the ownership of those values from one thread to another. Here is an example.

```rust
use std::thread;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(move || {
        println!("Here's a vector: {v:?}");
    });

    handle.join().unwrap();
}
```

Without the `move` keyword, the Rust compiler will infer the borrow checking. Since the `println` only need a reference, it will infer a reference borrow of `v` in closure. However, the out-of-order execution of thread making infer the lifetime of the reference impossible. So we need to force the closure to take ownership.

## Transfer Data Between Threads with Message Passing

Rust’s standard library provides an implementation of channels to accomplish message-sending concurrency.  
Channel is a general program concepts by which data is sent from one thread to another.

We use `mpsc::channel` to create a new channel. `mpsc` stands for *multiple producer, single consumer*. These means a channel can have multiple sanding ends that produce values but only one receiving end that consume those values.  
The return of this function is a tuple `[transmitter, receiver]`. Here is an example.

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let val = String::from("hi");
        tx.send(val).unwrap();
    });

    let received = rx.recv().unwrap();
    println!("Got: {received}");
}
```

Note the `move` keyword used in this example. We need the spawned thread to own the `tx` to be able to send messages through the channel.  
The `send` method returns a `Result<T, E>`. If the receiver has already be dropped and there's nowhere to send, the function will return an error.  
The receiver has `recv` and `try_recv` two methods. The `recv` will block the main thread's execution, wait until a value is sent down. It returns a `Result<T, E>`. If the transmitter closes, it will return an error. The `try_recv` doesn't block and return a `Result<T, E>` immediately: an `Ok` value holding a message if one is available and an `Err` value if there aren’t any messages this time.  

The `send` method will transfer the ownership if the type of the value doesn't implement the `Copy` trait.

### Creating Multiple Producers

We can clone the transmitter and transfer it to multiple thread.

```rust
    // --snip--

    let (tx, rx) = mpsc::channel();

    let tx1 = tx.clone();
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];

        for val in vals {
            tx1.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    thread::spawn(move || {
        let vals = vec![
            String::from("more"),
            String::from("messages"),
            String::from("for"),
            String::from("you"),
        ];

        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    for received in rx {
        println!("Got: {received}");
    }

    // --snip--
```

## Shared-State Concurrency

### Controlling Access with Mutexes

Mutex is an abbreviation for *mutual exclusion*, as in a mutex allows only one thread to access some data at any given time.  
Here is an example of using mutex in Rust.

```rust
use std::sync::Mutex;

fn main() {
    let m = Mutex::new(5);

    {
        let mut num = m.lock().unwrap();
        *num = 6;
    }

    println!("m = {m:?}");
}
```

We need to call `lock` to acquire the data. It will block the current thread.  
The call to `lock` would fail if another thread holding the lock panicked.  
Rust will mark this type of mutex **poisoned**. Other threads try to get this lock will return `Err(PoisonError)`.  
The `PoisonError` still hold the data `MutexGuard<T>`. Then Rust lets the owner to decide whether or not to use the protected value, since a panic of another thread may violate some guarantee of this data.

When we need multiple threads to share the same mutex, we can use `Arc<T>`. Notice that `Rc<T>` is not thread-safety. The `A` stands for *atomic*.

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();

            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}
```

Note that if you are doing simple numerical operations, there are types simpler than `Mutex<T>` types provided by the `std::sync::atomic` module of the standard library.   
These types provide safe, concurrent, atomic access to primitive types.

## Extensible Concurrency with Send and Sync

The `Send` marker trait indicates that ownership of values of the type implementing `Send` can be transferred between threads.  
Any type composed entirely of `Send` types is automatically marked as `Send` as well.

The `Sync` marker trait indicates that it is safe for the type implementing `Sync` to be referenced from multiple threads.   
In other words, any type `T` implements `Sync` if `&T` (an immutable reference to `T`) implements `Send`, meaning the reference can be sent safely to another thread.   
Similar to `Send`, primitive types all implement `Sync`, and types composed entirely of types that implement `Sync` also implement Sync.

The `Send` and `Sync` are marker traits, they don't have any methods to implement.  
Manually implementing these traits involves implementing unsafe Rust code.
