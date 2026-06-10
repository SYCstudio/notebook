# Chapter 13 Functional Language Features: Iterators and Closures

## Closures

Rust’s closures are anonymous functions you can save in a variable or pass as arguments to other functions.  
Unlike functions, closures can capture values from the scope in which they’re defined.

### Inferring and Annotating Closure Types

In most cases, the compiler can infer the types of a closure.  
However, we can still annotate them for better explicitness and clarity. Here is an example.

```rust
let expensive_closure = |num: u32| -> u32 {
	println!("calculating slowly...");
	thread::sleep(Duration::from_secs(2));
	num
};
```

Here is an another example that compare the syntax of closures and functions.

```rust
fn  add_one_v1   (x: u32) -> u32 { x + 1 }
let add_one_v2 = |x: u32| -> u32 { x + 1 };
let add_one_v3 = |x|             { x + 1 };
let add_one_v4 = |x|               x + 1  ;
```

The types of a closure can be inferred by the compiler. But those types should be the same from different source.  
Here is an example of using a closure in two different ways, which will give us an error when compiling.

```rust
let example_closure = |x| x;

let s = example_closure(String::from("hello"));
let n = example_closure(5);
```

### Capturing References or Moving Ownership

Closures can capture values from their environment in three ways: borrowing immutably, borrowing mutably, and taking ownership.  
The closure will decide which of these to use based on what the body of the function does with the captured values.

Here the first example is for immutable borrowing. In this example, the compiler can figure out that we only need the immutable reference of `list`.

```rust
fn main() {
    let list = vec![1, 2, 3];
    println!("Before defining closure: {list:?}");

    let only_borrows = || println!("From closure: {list:?}");

    println!("Before calling closure: {list:?}");
    only_borrows();
    println!("After calling closure: {list:?}");
}
```

Note that, because we can have multiple immutable references to `list` at the same time, `list` is still accessible from the code before the closure definition, after the closure definition but before the closure is called, and after the closure is called.

Next is the example for mutable borrowing. We use the `push` in the closure, so now the closure captures a mutable reference.

```rust
fn main() {
    let mut list = vec![1, 2, 3];
    println!("Before defining closure: {list:?}");

    let mut borrows_mutably = || list.push(7);

    borrows_mutably();
    println!("After calling closure: {list:?}");
}
```

Note that, we cannot `println! list` between the call and the definition of `borrows_mutably` closure, since there is a mutable reference, which is exclusive.

If you want to force the closure to take ownership of the values it uses in the environment even though the body of the closure doesn’t strictly need ownership, you can use the `move` keyword before the parameter list.  
This technique is mostly useful when passing a closure to a new thread to move the data so that it’s owned by the new thread.  
Here is an example.

```rust
use std::thread;

fn main() {
    let list = vec![1, 2, 3];
    println!("Before defining closure: {list:?}");

    thread::spawn(move || println!("From thread: {list:?}"))
        .join()
        .unwrap();
}
```

### Moving Captured Values Out of Closures

The closure body can do many things: Move a captured value out of the closure, mutate the captured value, neither move nor mutate the value, or capture nothing from the environment to begin with.  
The way above affects which *traits* the closure implements. Traits are how functions and structs can specify what kinds of closures they can use.  

Closures will automatically implement one, two, or all three of the following `Fn` traits, in an additive fashion.

1. `FnOnce`: For closures that can be called once. All the closure will implement at least this trait since all closure can be called. A closure that moves captured values out of its body will only implement `FnOnce` and none of the other `Fn` traits because it can only be called once.  
2. `FnMut`: For closures that don’t move captured values out of their  body but might mutate the captured values. They can be called more than once.  
3. `Fn`: For closures that don’t move captured values out of their body  and don’t mutate captured values. These closures can be called more than once without mutating their environment

Here is an example from `Option<T>`'s `unwrap_or_else`, which uses a closure that required to implement `FnOnce` trait. It means `F` must be able to be called once, take no arguments and return a `T`. The body of the `unwrap_or_else` ensures that the `F` will be called no more than once.

```rust
impl<T> Option<T> {
    pub fn unwrap_or_else<F>(self, f: F) -> T
    where
        F: FnOnce() -> T
    {
        match self {
            Some(x) => x,
            None => f(),
        }
    }
}
```

> If what we want to do doesn’t require capturing a value from the environment, we can  use the name of a function rather than a closure where we need something that implements one of the `Fn` traits. For example, on an `Option<Vec<T>>` value, we could call `unwrap_or_else(Vec::new)` to get a new, empty vector if the value is `None`. The compiler automatically implements whichever of the `Fn` traits is applicable for a function definition.


## Processing a Series of Items with Iterators

The iterator pattern allows you to perform some task on a sequence of items in turn.  
An iterator is responsible for the logic of iterating over each item and determining when the sequence has finished.  
Rust's iterators are lazy, means they have no effect until we call and consume the them.

All the iterators implement the `Iterator` trait. It looks like:

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
    // methods with default implementations elided
}
```

The syntax of `type Item` and `Self::Item` defines an associated types with this trait.  
In this case, it means that the implementing the `Iterator` trait requires that we also define an `Item` type, which is used in the return type of the `next` method.  
Compare to template, the associated type only allows a single specific type to be implemented, making the API useful. Here is an example.

```rust
struct Counter {
    value: u32,
}
impl Iterator for Counter {
    type Item = u32; // specify the Item is u32
    fn next(&mut self) -> Option<Self::Item> {
        self.value += 1;

        if self.value < 5 {
            Some(self.value)
        } else {
            None
        }
    }
}
```

Note that the `next` will consume the `self` and change it, so the signature in `next` is `&mut self`.  
The values we got from the calls to `next` are immutable reference to the values in the vector. If we want to create an iterator that takes ownership and return owned value, we need to call `into_iter` instead of `iter`. Similarly, if we want to iterate over mutable references, we can call `iter_mut` instead of `iter`.

| Method       | Produces Type | Ownership      | Consumes Original Collection | Can Modify Original Collection | Use Case                    |
|--------------|---------------|----------------|------------------------------|-------------------------------|-----------------------------|
| `iter()`     | `&T`          | Borrow         | No                           | No                            | Read-only access            |
| `into_iter()`| `T`           | Transfer       | Yes                          | N/A                           | Need to own elements        |
| `iter_mut()` | `&mut T`      | Mutable borrow | No                           | Yes                           | Need to modify elements     |
### Ownership of Iterator

Here is an example of using `next` manually and using `for` to iterating over iterator.  

```rust
// using for
let v1 = vec![1, 2, 3];
let v1_iter = v1.iter();
for val in v1_iter {
	println!("Got: {val}");
}

// using next manually
let v1 = vec![1, 2, 3];

let mut v1_iter = v1.iter();

assert_eq!(v1_iter.next(), Some(&1));
assert_eq!(v1_iter.next(), Some(&2));
assert_eq!(v1_iter.next(), Some(&3));
assert_eq!(v1_iter.next(), None);
```

Note that we need to use `mut v1_iter` in the `next` scenario, but not in the `for` scenario.  
This is because the `for` loop took ownership and made it mutable behind the scenes. The internal implementation can be something like this:

```rust
let mut iter =
	IntoIterator::into_iter(v1_iter);

loop {
	match iter.next() {
		Some(val) => {
			println!("{val}");
		}
		None => break,
	}
}
```

Note that, the mutability of variables in Rust belongs to *binding* not the *value* itself.  
We can change the mutability when transfer the ownership. Here is a valid example.

```rust
let a = vec![1,2,3];
let mut b = a;
b.push(4);
```

### Methods of Iterators

The standard Rust API provides many methods for iterators.  
#### Consuming Adaptors

Consuming adaptors are methods that call `next`, since calling them use up the iterator. Here is an example use the `sum` method.

```rust
let v1 = vec![1, 2, 3];
let v1_iter = v1.iter();
let total: i32 = v1_iter.sum();
assert_eq!(total, 6);
```

#### Iterator Adaptors

Iterator adaptors are methods that don't consume the iterator. Instead, they produce different iterators by changing some aspect of the original iterator.  
Here is an example. We use the `map` to modify the inner value. However, since the `iter` in Rust is lazy, it will only have effect after we call the `collect`.

```rust
let v1: Vec<i32> = vec![1, 2, 3];
let v2: Vec<_> = v1.iter().map(|x| x + 1).collect();
assert_eq!(v2, vec![2, 3, 4]);
```

We can chain multiple calls to iterator adapters to perform complex actions in a readable way

