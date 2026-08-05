# Chapter 20 Advanced Features

## Unsafe Rust

Rust has *unsafe rust* gives us extra superpowers.  
Two reasons: static analysis is conservative; the underlying computer hardware is inherently unsafe.

Use the `unsafe` keyword and start a new block to switch to unsafe Rust.  
We can take five actions:

1. Dereference a raw pointer  
2. Call an unsafe function or method  
3. Access or modify a mutable static variable  
4. Implement an unsafe trait  
5. Access fields of `unions`

`unsafe` doesn't turn off the borrow checker or disable any of Rust's other safety checks.  
`unsafe` doesn't mean the code inside the block is necessarily dangerous, or that it will definitely have memory safety problems.  
To isolate unsafe code as much as possible, it’s best to enclose such code within a safe abstraction and provide a safe API.

### Dereferencing a Raw Pointer

Raw pointers can be immutable or mutable, `*const T` and `*mut T`.  
In the context of raw pointers, immutable means that the pointer can’t be directly assigned to after being dereferenced.

1. Raw pointers are allowed to ignore the borrowing rules. We can have both immutable and mutable pointer or multiple mutable pointers.  
2. Raw pointers are not guaranteed to point to valid memory.  
3. Raw pointers are allowed to be null.  
4. Raw pointers do not implement any automatic cleanup.

It is used for greater performance, or the ability to interface with another language, or hardware.

```rust
    let mut num = 5;

    let r1 = &raw const num;
    let r2 = &raw mut num;

    unsafe {
        println!("r1 is: {}", *r1);
        println!("r2 is: {}", *r2);
    }
```

Note that the above code is not all in the `unsafe` block. We can create raw pointer in safe code. We just can't dereference them.

### Calling an Unsafe Function or Method

Putting `unsafe` keyword before can make unsafe functions and methods.

We can only call unsafe functions in unsafe block. Never the less, we still need to use an `unsafe` block to perform unsafe operations in the body of unsafe functions.  
In practice, wrapping unsafe code in a safe function is a common abstraction.

```rust
use std::slice;

fn split_at_mut(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = values.len();
    let ptr = values.as_mut_ptr();

    assert!(mid <= len);

    unsafe {
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

We sometimes need to interact with code written in another language.  
Rust has a keyword `extern` to use of a *Foreign Function Interface(FFI)*, which enable a different programming language to call those functions.  
Here is an example that declare and call a C function.

```rust
unsafe extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("Absolute value of -3 according to C: {}", abs(-3));
    }
}
```

Every item declared within an unsafe extern block is implicitly unsafe. However, some FFI functions are safe to call.  
We can use the safe keyword to say that this specific function is safe to call even though it is in an unsafe extern block.  
Then we can call it without an unsafe block.

We can also use `extern` to create an interface that allows other languages to call Rust functions.  
Instead of creating a whole extern block, we add the `extern` keyword and specify the ABI to use just before the `fn` keyword for the relevant function.   
We also need to add an `#[unsafe(no_mangle)]` annotation to tell the Rust compiler not to mangle the name of this function.

> Mangling is when a compiler changes the name we’ve given a function to a different name that contains more information for other parts of the compilation process to consume but is less human readable.    
> This is unsafe because there might be name collisions across libraries without the built-in mangling

```rust
unsafe extern "C" {
    safe fn abs(input: i32) -> i32;
}

fn main() {
    println!("Absolute value of -3 according to C: {}", abs(-3));
}
```

### Accessing or Modifying a Mutable Static Variable

In Rust, global variables are called *static* variables.  
Static variables can only store references with the 'static lifetime, which means the Rust compiler can figure out the lifetime and we aren’t required to annotate it explicitly.
Static variables are similar to constants. However, a subtle difference is that, values in a static variable have a fixed address in memory, while constants are allowed to duplicate their data whenever they’re used.    
Another difference is that static value can be mutable, however, which is unsafe.

```rust
static mut COUNTER: u32 = 0;

/// SAFETY: Calling this from more than a single thread at a time is undefined
/// behavior, so you *must* guarantee you only call it from a single thread at
/// a time.
unsafe fn add_to_count(inc: u32) {
    unsafe {
        COUNTER += inc;
    }
}

fn main() {
    unsafe {
        // SAFETY: This is only called from a single thread in `main`.
        add_to_count(3);
        println!("COUNTER: {}", *(&raw const COUNTER));
    }
}
```

Whenever we write an unsafe function, it is idiomatic to write a comment starting with `SAFETY` and explaining what the caller needs to do to call the function safely.   
Likewise, whenever we perform an unsafe operation, it is idiomatic to write a comment starting with `SAFETY` to explain how the safety rules are upheld.

Additionally, the compiler will deny by default any attempt to create references to a mutable static variable through a compiler lint.   
You must either explicitly opt out of that lint’s protections by adding an `#[allow(static _mut_refs)]` annotation or access the mutable static variable via a raw pointer created with one of the raw borrow operators.

### Implementing an Unsafe Trait

A trait is unsafe when at least one of its methods has some invariant that the compiler can't verify.

```rust
unsafe trait Foo {
    // methods go here
}

unsafe impl Foo for i32 {
    // method implementations go here
}
```

### Accessing Fields of a Union

A `union` is similar to a struct, but only one declared field is used in a particular instance at one time.  
Unions are primarily used to interface with unions in C code.   
Accessing union fields is unsafe because Rust can’t guarantee the type of the data currently being stored in the union instance.

### Using Miri to Check Unsafe Code

We can use `miri` , an official Rust tool to check the unsafe code is actually safe and correct.  
Miri is a dynamic tool that works at runtime, compare to the borrow checker which is a static tool that works at compile time.

Using Miri requires a nightly build of Rust.  
You can install both a nightly version of Rust and the Miri tool by typing `rustup +nightly component add miri`.

## Advanced Traits

### Defining Traits with Associated Types

Associated types connect a type placeholder with a trait such that the trait method definitions can use these placeholder types in their signatures.  
That way, we can define a trait that uses some types without needing to know exactly what those types are until the trait is implemented.  
One example is the `Iterator` trait, which has a `type Item` as associated types.

The associated types look similar to generics. However, they are different.  
When use generics, we must annotate the types in each implementation. When a trait has a generics parameter, it can be implemented for a type multiple times. This is not needed when we use associated types.

### Using Default Generic Parameters and Operator Overloading

We can specify a default concrete type for generic type, with the `<PlaceHolderType=ConcreteType>` syntax.

```rust
trait Add<Rhs=Self> {
    type Output;

    fn add(self, rhs: Rhs) -> Self::Output;
}
```

We'll use default type parameters in two main ways:

1. To extend a type without breaking existing code  
2. To allow customization in specific cases most users won’t need

### Disambiguating Between Identically Named Methods

Traits may have same name methods.  
When calling methods with same name, we need to tell Rust which one we want to use.

```rust
trait Pilot {
    fn fly(&self);
}

trait Wizard {
    fn fly(&self);
}

struct Human;

impl Pilot for Human {
    fn fly(&self) {
        println!("This is your captain speaking.");
    }
}

impl Wizard for Human {
    fn fly(&self) {
        println!("Up!");
    }
}

impl Human {
    fn fly(&self) {
        println!("*waving arms furiously*");
    }
}
```

In the above example, when we call `fly`, the compiler defaults to calling the method that is directly implemented on the type.  
To use the method in trait, we need to explicit syntax to specify.

```rust
fn main() {
    let person = Human;
    Pilot::fly(&person);
    Wizard::fly(&person);
    person.fly();
}
```

The above example takes a `self` parameter. However, associated functions that are not methods don't have it. We need to use fully qualified syntax.

```rust
trait Animal {
    fn baby_name() -> String;
}

struct Dog;

impl Dog {
    fn baby_name() -> String {
        String::from("Spot")
    }
}

impl Animal for Dog {
    fn baby_name() -> String {
        String::from("puppy")
    }
}

fn main() {
    println!("A baby dog is called a {}", <Dog as Animal>::baby_name());
}
```

### Using Supertraits

A trait definition that depends on another trait.

```rust
use std::fmt;

trait OutlinePrint: fmt::Display {
    fn outline_print(&self) {
        let output = self.to_string();
        let len = output.len();
        println!("{}", "*".repeat(len + 4));
        println!("*{}*", " ".repeat(len + 2));
        println!("* {output} *");
        println!("*{}*", " ".repeat(len + 2));
        println!("{}", "*".repeat(len + 4));
    }
}
```

### Implementing External Traits with the Newtype Pattern

We have mentioned the orphan rule that states we’re only allowed to implement a trait on a type if either the trait or the type, or both, are local to our crate.  
We can use the newtype pattern to get around this restriction, which involves creating a new type in a tuple struct..  
There is no runtime performance penalty for using this pattern, and the wrapper type is elided at compile time.

```rust
use std::fmt;

struct Wrapper(Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}

fn main() {
    let w = Wrapper(vec![String::from("hello"), String::from("world")]);
    println!("w = {w}");
}
```

If we wanted the new type to have every method the inner type has, implementing the `Deref` trait on the it to return the inner type would be a solution

## Advanced Types

### Type Safety and Abstraction with the Newtype Pattern

We can use newtype to: enforce the values are never be confused; abstract away some implementation details, only expose a public API.

### Type Synonyms and Type Aliases

We can use type aliases to give an existing type another name.  
`type Kilometer = i32;` where `kilometer` is a synonym for `i32`, rather than a separate, new type, unlike newtype pattern.

### The Never Type That Never Returns

Rust has a special type named `!` that’s known in type theory lingo as the empty type because it has no values.   
We prefer to call it the never type because it stands in the place of the return type when a function will never return.

Here is an example

```rust
fn bar() -> ! {
    // --snip--
}
```

The `continue` has a `!` value. So the following match arms will compile well.

```rust
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };
```

The formal way of describing this behavior is that expressions of type `!` can be coerced into any other type.  
The never type is useful with the `panic!` macro as well.  
One final expression that has the type `!` is a loop.

### Dynamically Sized Types and the Sized Trait

Dynamically sized types(DSTs) use values whose size we can know only at runtime.  
However, Rust needs to know certain details about its types when compile.  
In general, Rust's DSTs have an extra bit of metadata that stores the size of the dynamic information.

Every trait is a dynamically sized type we can refer to by using the name of the trait. Such as `&dyn Trait` and `Box<dyn Trait>`.

To work with DSTs, Rust provides the `Sized` trait to determine whether a type’s size is known at compile time.   
This trait is automatically implemented for everything whose size is known at compile time.   
In addition, Rust implicitly adds a bound on `Sized` to every generic function. That is 

```rust
fn generic<T>(t: T) {
    // --snip--
}
```

is actually treated as though we had written this:

```rust
fn generic<T: Sized>(t: T) {
    // --snip--
}
```

By default, generic functions will work only on types that have a known size at compile time.   
However, you can use the following special syntax to relax this restriction:

```rust
fn generic<T: ?Sized>(t: &T) {
    // --snip--
}
```

A trait bound on `?Sized` means “T may or may not be Sized,” and this notation overrides the default that generic types must have a known size at compile time. So we change the `T` to `&T` in function's parameter.  
The `?Trait` syntax with this meaning is only available for `Sized`, not any other traits.

## Advanced Functions and Closures

### Function Pointers

We can pass regular functions to functions.  
Functions coerce to the type `fn`, which is called a *function pointer*.  
The syntax is similar to closures.

```rust
fn add_one(x: i32) -> i32 {
    x + 1
}

fn do_twice(f: fn(i32) -> i32, arg: i32) -> i32 {
    f(arg) + f(arg)
}

fn main() {
    let answer = do_twice(add_one, 5);

    println!("The answer is: {answer}");
}
```

Unlike closures, `fn` is a type rather than a trait, so we specify `fn` as the parameter type directly rather than declaring a generic type parameter with one of the `Fn` traits as a trait bound.  
Function pointers implement all three of the closure traits (`Fn`, `FnMut`, and `FnOnce`), meaning you can always pass a function pointer as an argument for a function that expects a closure.  
In practice, we write functions use a generic type and one of the closure traits so that your functions can accept either functions or closures.

### Returning Closures

We can't return closures directly because closures are represented by traits.  
We can use the `impl Trait` syntax to return any function type.

```rust
fn returns_closure() -> impl Fn(i32) -> i32 {
    |x| x + 1
}
```

Each closure is also its own distinct type.  
If we need to work with multiple functions that have same signature but different implementations, we will need to use a trait object for them.

```rust
fn main() {
    let handlers = vec![returns_closure(), returns_initialized_closure(123)];
    for handler in handlers {
        let output = handler(5);
        println!("{output}");
    }
}

fn returns_closure() -> Box<dyn Fn(i32) -> i32> {
    Box::new(|x| x + 1)
}

fn returns_initialized_closure(init: i32) -> Box<dyn Fn(i32) -> i32> {
    Box::new(move |x| x + init)
}
```


## Macros

### The Difference Between Macros and Functions

Fundamentally, macros are a way of writing code that writes other code.  

A function signature must declare the number and type of parameters the function has.   
Macros, on the other hand, can take a variable number of parameters.  
Macros are expanded before the compiler interprets the meaning of the code. 

Downside: more complex, difficult to read, understand and read.

### Declarative Macros for General Metaprogramming

Declarative macros allow you to write something similar to a Rust match expression.   
We can use `macro_rules!` macro to build macros. Here is an example of simplified definition of the `vec!` macro.

```rust
#[macro_export]
macro_rules! vec {
    ( $( $x:expr ),* ) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}
```

The `#[macro_export]` annotation indicates that this macro should be made available whenever the crate in which the macro is defined is brought into scope.

### Procedural Macros for Generating Code from Attributes

Procedural macros accept some code as an input, operate on that code, and produce some code as an output rather than matching against patterns and replacing the code with other code as declarative macros do.  
It has three kinds: custom `derive`, attribute-like, and function-like. Here is an example

```rust
use proc_macro::TokenStream;

#[some_attribute]
pub fn some_name(input: TokenStream) -> TokenStream {
}
```

It takes a `TokenStream` as an input and produces a `TokenStream` as an output.
Procedural macros need to be in their own crate.
#### Custom derive Macros

Here is an example that create a `hello_macro`.  
First is the main code that use the trait.

```rust
use hello_macro::HelloMacro;
use hello_macro_derive::HelloMacro;

#[derive(HelloMacro)]
struct Pancakes;

fn main() {
    Pancakes::hello_macro();
}
```

We need to declare the macro in independent crate, in current Rust version. In the future, this restriction may be removed.  
Here is the implementation of `hello_macro`

```rust
use proc_macro::TokenStream;
use quote::quote;

#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    // Construct a representation of Rust code as a syntax tree
    // that we can manipulate.
    let ast = syn::parse(input).unwrap();

    // Build the trait implementation.
    impl_hello_macro(&ast)
}

fn impl_hello_macro(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;
    let generated = quote! {
        impl HelloMacro for #name {
            fn hello_macro() {
                println!("Hello, Macro! My name is {}!", stringify!(#name));
            }
        }
    };
    generated.into()
}
``` 

The `syn` crate parses Rust code from a string into a data structure that we can perform operations on.  
The `quote` crate turns `syn` data structure back into Rust code.  

Note that we use `unwrap` to cause the function to panic if the parsing fails.  
This is necessary, because we can only return `TokenStream`, rather than `Result<T, E>`.  
In production, there should be some specific error message.

The `quote!` macro allow us to replace the value in the variable's name.  
The `stringify!` macro turns the expression into a string literal at compile time. It is different from `format!` or `println!` , which evaluate the expression and then turn the result into `String.`

#### Attribute-Like Macros

Attribute-like macros allow us to create new attributes. It can be applied to not only structs and enums, but also functions.  
Here is an example.

```rust
#[route(GET, "/")]
fn index() {...}

#[proc_macro_attribute] pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {...}
```

#### Function-Like Macros

Function-like macros define macros that look like function calls.  
They can only be defined using the match-like syntax.

