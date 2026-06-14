# Chapter 15 Smart Pointers

In Rust, *references* borrow data, while *smart pointers* own the data they point to.  
Smart pointers are usually implemented using struct, with `Deref` and `Drop` trait implemented.   
`Deref` allows it to behave like a reference. `Drop` allows to run custom clean up code when the smart pointer goes out of the scope.

## Using `Box<T>` to Point to Data on the Heap

`Box<T>` is the most straightforward smart pointer. It allows us to store data on the heap rather than the stack.  
We use it most often in the following situations:

1. When you have a type whose size can’t be known at compile time, and you  want to use a value of that type in a context that requires an exact size.  
2. When you have a large amount of data, and you want to transfer ownership but ensure that the data won’t be copied when you do so.  
3. When you want to own a value, and you care only that it’s a type that  implements a particular trait rather than being of a specific type.

Here is an example that create a `Box<T>`

```rust
fn main() {
    let b = Box::new(5);
    println!("b = {b}");
}
```

We can use `Box` to define recursive types. Here is an example:

```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}

use crate::List::{Cons, Nil};

fn main() {
    let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));
}
```

## Treating Smart Pointers Like Regular References

Implementing the `Deref` trait allows us to customize the behavior of the *dereference operator `*`* .  
Here is an example using the normal reference and smart pointer.

```rust
// normal reference
fn main() {
    let x = 5;
    let y = &x;

    assert_eq!(5, x);
    assert_eq!(5, *y);
}
// box
fn main() {
    let x = 5;
    let y = Box::new(x); // y is an instance of a box pointing to a copied value of x

    assert_eq!(5, x);
    assert_eq!(5, *y);
}
```

We can implement the `Deref` trait to our own struct and make it capable with the `*` operator. Here is an example:

```rust
struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(x: T) -> MyBox<T> {
        MyBox(x)
    }
}

use std::ops::Deref;

impl<T> Deref for MyBox<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

fn main() {
    let x = 5;
    let y = MyBox::new(x);

    assert_eq!(5, x);
    assert_eq!(5, *y); // actually *(y.deref())
}
```

Rust substitutes the `*` operator with a call to the `deref` method and then a plain dereference so that we don’t have to think about whether we need to call the deref method.

### Using Deref Coercion in Functions and Methods

*Deref coercion* converts a reference to a type into a reference to another type.  
We have already see the example of converting `&String` to `&str`, since the `String` implements the `Deref` trait returns `&str`.  
It happens automatically when we pass a reference to a particular type’s value as an argument to a function or method that doesn’t match the parameter type in the function or method definition.  
Here is an example using the above `MyBox<T>`

```rust
fn hello(name: &str) {
    println!("Hello, {name}!");
}
fn main() {
    let m = MyBox::new(String::from("Rust"));
    hello(&m);
}
```

Because we implement `Deref` trait for `MyBox`, Rust can turn `&m` the `&MyBox<String>` into `&String`. Then again turn the `&String` into `&str` since the standard library implement it.  
Without the deref coercion, the code will be more complicated like `hello(&(*m)[..]);`.

### Handling Deref Coercion with Mutable References

`Deref` trait is for override the `*` operator on immutable reference, `DerefMut` trait is for mutable reference.

Rust does deref coercion in three cases:

1. From `&T` to `&U` when `T: Deref<Target=U>`
2. From `&mut T` to `&mut U` when `T: DerefMut<Target=U>`
3. From `&mut T` to `&U` when `T: Deref<Target=U>`

Note that, the third case indicate that Rust will coerce a mutable reference to an immutable one. But the reverse is not possible.

## Running Code on Cleanup with the Drop Trait

`Drop` lets us customize what happens when a value is about to go out of scope.  
We do not need to call the `drop` method explicitly. Rust automatically called `drop` for us when our instances went out of scope, calling the code we specified.  
Variables are dropped in the reverse order of their creation.  

Rust doesn't let us call the `Drop` trait's `drop` method manually.   
If we want to force a value to be dropped before the end of its scope, we have to call the `std::mem::drop` function provided by the standard library.

## `Rc<T>` the Reference-Counted Smart Pointer

We can enable multiple ownership explicitly by using the `Rc<T>`, for *reference counting*.   
It keeps track of the number of references to a value, to determine whether the value is still in use.  
Note that `Rc<T>` is only for use in single-threaded scenarios.

Here is an example, where two list share a sub-list in common.

```rust
enum List {
    Cons(i32, Rc<List>),
    Nil,
}

use crate::List::{Cons, Nil};
use std::rc::Rc;

fn main() {
    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));
    let b = Cons(3, Rc::clone(&a));
    let c = Cons(4, Rc::clone(&a));
}
```

Note that we call `Rc::clone` to create `b` and `c`.   
The implementation of `Rc::clone` doesn’t make a deep copy of all the data. It only increments the reference count.

## `RefCell<T>` and the Interior Mutability Pattern

*Interior mutability* is a design pattern in Rust that allows you to mutate data even when there are immutable references to that data.   
Normally, this action is disallowed by the borrowing rules. We  need to uses `unsafe` code inside a data structure to bend Rust's usual rules.

`RefCell<T>` type represents single ownership over the data it holds.  
For `Box<T>`, the borrowing rules' invariants are enforced at compile time. Break the rules will get a compiler error.  
But for `RefCell<T>`, these invariants are enforced *at runtime*. Break the rules will panic and exit at runtime.

Here is an example using the `RefCell<T>`. The method in trait is defined in immutable way, but we need it be mutable in testing.

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    struct MockMessenger {
        sent_messages: RefCell<Vec<String>>,
    }

    impl MockMessenger {
        fn new() -> MockMessenger {
            MockMessenger {
                sent_messages: RefCell::new(vec![]),
            }
        }
    }

    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            self.sent_messages.borrow_mut().push(String::from(message));
        }
    }

    #[test]
    fn it_sends_an_over_75_percent_warning_message() {
        // --snip--

        assert_eq!(mock_messenger.sent_messages.borrow().len(), 1);
    }
}
```

With `RefCell<T>`, we can use the `borrow` , which returns the smart pointer type `Ref<T>`, and `borrow_mut`, which returns the smart pointer type `RefMut<T>`.  
The `RefCell<T>` keeps track of how many `Ref<T>` and `RefMut<T>` smart pointers are currently active.  
Just like the compile-time borrowing rules, `RefCell<T>` lets us have many immutable borrows or one mutable borrow at any point in time.

### Allowing Multiple Owners of Mutable Data

It we have an `Rc<T>` that holds a `RefCell<T>`, we can get a value that can have multiple owners and that we can mutate.  
Here is an example.

```rust
#[derive(Debug)]
enum List {
    Cons(Rc<RefCell<i32>>, Rc<List>),
    Nil,
}

use crate::List::{Cons, Nil};
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    let value = Rc::new(RefCell::new(5));

    let a = Rc::new(Cons(Rc::clone(&value), Rc::new(Nil)));

    let b = Cons(Rc::new(RefCell::new(3)), Rc::clone(&a));
    let c = Cons(Rc::new(RefCell::new(4)), Rc::clone(&a));

    *value.borrow_mut() += 10;

    println!("a after = {a:?}");
    println!("b after = {b:?}");
    println!("c after = {c:?}");
}
```

## Reference Cycles Can Leak Memory

 Memory leaks is difficult, but not impossible in Rust's memory safety guarantees. They are memory safe in Rust.  
 Here is an example.
 
```rust
use crate::List::{Cons, Nil};
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
enum List {
    Cons(i32, RefCell<Rc<List>>),
    Nil,
}

impl List {
    fn tail(&self) -> Option<&RefCell<Rc<List>>> {
        match self {
            Cons(_, item) => Some(item),
            Nil => None,
        }
    }
}
fn main() {
    let a = Rc::new(Cons(5, RefCell::new(Rc::new(Nil))));

    println!("a initial rc count = {}", Rc::strong_count(&a));
    println!("a next item = {:?}", a.tail());

    let b = Rc::new(Cons(10, RefCell::new(Rc::clone(&a))));

    println!("a rc count after b creation = {}", Rc::strong_count(&a));
    println!("b initial rc count = {}", Rc::strong_count(&b));
    println!("b next item = {:?}", b.tail());

    if let Some(link) = a.tail() {
        *link.borrow_mut() = Rc::clone(&b);
    }

    println!("b rc count after changing a = {}", Rc::strong_count(&b));
    println!("a rc count after changing a = {}", Rc::strong_count(&a));

    // Uncomment the next line to see that we have a cycle;
    // it will overflow the stack.
    // println!("a next item = {:?}", a.tail());
}
```

### Preventing Reference Cycles Using `Weak<T>`

Calling `Rc::clone` increase the `strong_count` of an `Rc<T>` instance. And an `Rc<T>` instance is only cleaned up if its `strong_count` is 0.  
We can create a weak reference by calling `Rc::downgrade`.  
*Strong references* are how you can share ownership of  an `Rc<T>` instance. *Weak* references don't express an ownership relationship.

Calling `Rc::downgrade` will get a smart pointer of type `Weak<T>`. It will increase the `weak_count` by 1.  
The value that `Weak<T>` reference might have been dropped. So to do anything with the value that a `Weak<T>` pointing to , we must make sure the value still exists.  
We can call the `upgrade` method on a `Weak<T>` instance. It will return an `Option<Rc<T>>`, which indicate whether the value still exists.

Here is an example using `Weak<T>` in a tree struct.

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

#[derive(Debug)]
struct Node {
    value: i32,
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}
fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });

    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());

    let branch = Rc::new(Node {
        value: 5,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());
}
```
