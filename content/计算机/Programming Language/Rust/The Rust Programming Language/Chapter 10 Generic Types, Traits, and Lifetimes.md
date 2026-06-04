# Chapter 10 Generic Types, Traits, and Lifetimes

## Generic Data Types

### In Function Definitions

We place the generic types in the signature of the function, where we would usually specify the data types of parameters and return value.  
Here is an example. However, this example will not compile successfully. The compiler will notice us that the type parameter `T` should have trait `PartialOrd` because we apply the `>` operator in the function body.

```rust
fn largest<T>(list: &[T]) -> &T {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let result = largest(&number_list);
    println!("The largest number is {result}");

    let char_list = vec!['y', 'm', 'a', 'q'];

    let result = largest(&char_list);
    println!("The largest char is {result}");
}
```

### In Struct Definitions

The generic type definition is similar to the function definitions, using the same `<>` syntax. Here is an example.

```rust
struct Point<T> {
    x: T,
    y: T,
}

fn main() {
    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.0, y: 4.0 };
}
```

### In Enum Definitions

We already see two examples of generic used in enum.

```rust
enum Option<T> {
	Some(T),
	None,
};
enum Result<T, E> {
	Ok(T),
	Err(E),
};
```

### In Methods Definitions

We can implement methods over the structs and enums which have generic definitions.  
Here is an example.

```rust
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

fn main() {
    let p = Point { x: 5, y: 10 };

    println!("p.x = {}", p.x());
}
```

Note that in the above example, we need place `impl<T> Point<T>`  rather than `impl Point<T>`.  
This is because we need to identifier the type `T` in this scope is a generic type, instead of a concrete type.  
The parameter `T` after the `impl` imply that the methods declared in this scope is implemented for all the possible `T` instance.

We can use a different name in the `impl` block. The code snipper followed is same as the code above.

```rust
struct Point<T> {
    x: T,
    y: T,
}

impl<U> Point<U> {
    fn x(&self) -> &U {
        &self.x
    }
}
```

We can also specify constraints on generic types when defining methods on the type. Here is an example.

```rust
impl Point<f64> {
    fn distance(&self) -> f64 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}
```

Generic type parameters in a struct definition aren’t always the same as those you use in that same struct’s method signatures.   
Here is an example, where we mix the type of the struct and the parameter of methods.

```rust
struct Point<X1, Y1> {
    x: X1,
    y: Y1,
}

impl<X1, Y1> Point<X1, Y1> {
    fn mixup<X2, Y2>(self, other: Point<X2, Y2>) -> Point<X1, Y2> {
        Point {
            x: self.x,
            y: other.y,
        }
    }
}

fn main() {
    let p1 = Point { x: 5, y: 10.4 };
    let p2 = Point { x: "Hello", y: 'c' };

    let p3 = p1.mixup(p2);

    println!("p3.x = {}, p3.y = {}", p3.x, p3.y);
}
```

In `p1`, its type is `<i32, f64>`; in `p2` its type is `<&str, char>`. The `mixup` method takes the first of `p1` and the second of `p2`, combining create a `<i32, char>` the `p3`.  
Here, the generic parameters `X1` and `Y1` are declared after `impl` because they go with the struct definition. The generic parameters `X2` and `Y2` are declared after `fn mixup` because they’re only relevant to the method.

### Performance of Code Using Generics

Rust promise that programs that use generics will run as fast as that use concrete types.  
It accomplishes this by performing monomorphization of the code using generics at compile time.  
Monomorphization is the process of turning generic code into specific code by filling in the concrete types that are used when compiled.

## Defining Shared Behavior with Traits

`trait` defines the functionality a particular type has. It is similar to the `interface` abstraction in some other languages, but with some differences.  
We can use `trait bounds` to specify that a generic type can be any type that has certain behavior.

### Defining a Traits

Trait definitions are a way to group method signatures together to define a set of behaviors necessary to accomplish some purpose.  
Here is an example.

```rust
pub trait Summary {
    fn summarize(&self) -> String;
}
```

Note that after the method signature, we use a semicolon instead of an implementation within curly brackets.  
Each type implementing this trait must provide its own custom behavior for the body of the method.

### Implementing a Trait on a Type

Here is an example implementing the above `Summary` trait. Note that we use the `impl <Trait> for <Struct>` syntax.

```rust
pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

pub struct SocialPost {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub repost: bool,
}

impl Summary for SocialPost {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}
```

We need to bring the trait into scope as well as the types, when we want to use them.

```rust
use aggregator::{SocialPost, Summary};

fn main() {
    let post = SocialPost {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        repost: false,
    };

    println!("1 new post: {}", post.summarize());
}
```

One restriction to note is that we can implement a trait on a type only if either the trait or the type, or both, are local to our crate.  
We cannot implement external traits on external types (for example, `Display` traits on `Vec<T>`).  
This restriction is part of a property called *coherence*, and more specifically the *orphan rule*, so named because the parent type is not present.  
This rule ensures that other people’s code can’t break your code and vice versa.

### Using Default Definitions

We can define default actions for the traits methods. Here is an example.

```rust
pub trait Summary {
    fn summarize(&self) -> String {
        String::from("(Read more...)")
    }
}
```

Leaving the definition of the concrete type empty, we can use this default method in the concrete type.  
Or we can overwrite the method. The syntax for overriding a default implementation is the same as the syntax for implementing a trait method that doesn’t have a default implementation.

In the implementation of default method, we can call other method even if those methods don't have a default implementation. Here is an example.

```rust
pub trait Summary {
    fn summarize_author(&self) -> String;

    fn summarize(&self) -> String {
        format!("(Read more from {}...)", self.summarize_author())
    }
}
```

### Using Traits as Parameters

We can use traits to define functions that accept many different types. Here is an example.

```rust
pub fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}
```

Note that we use the `impl` keyword to specify this parameter can accept any type that implement this trait.

#### Trait Bound Syntax

The `impl Trait` syntax works for straightforward cases but is actually syntax sugar for a longer form known as a *trait bound*; it looks like this

```rust
pub fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}
```

When come to more parameter, this syntax allow us to express more complexity.  
The following code allows the `item1` and `item2` can have different types but both implement the `Summary` trait.

```rust
pub fn notify(item1: &impl Summary, item2: &impl Summary) {}
```

If we want to force their type to be same, we should use a trait bound.

```rust
pub fn notify<T: Summary>(item1: &T, item2: &T) {}
```

#### Multiple Trait Bounds with the + Syntax

We can specify more than one trait bound by using the `+` syntax. Here is an example.

```rust
pub fn notify(item: &(impl Summary + Display)) {}
pub fn notify<T: Summary + Display>(item: &T) {}
```

#### Clearer Trait Bounds with where Clauses

Using too many trait bounds will make the code hard to read.  
Rust introduces a `where` clause after the function signature to make it more clear.  

```rust
fn some_function<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) -> i32 {}
// same as
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug,
{}
```

### Returning Types That Implement Traits

We can also use the `impl Trait` syntax in the return position to return a value of some type that implements a trait. Here is an example

```rust
fn returns_summarizable() -> impl Summary {
    SocialPost {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        repost: false,
    }
}
```

However, even if we use the `impl Trait`, we can only return a single type. This is due to the restrictions around how the `impl Trait` syntax is implemented in the compiler.   
Here is an example that compile unsuccessfully, where we try to return different types in different `match` arms.

```rust
fn returns_summarizable(switch: bool) -> impl Summary {
    if switch {
        NewsArticle {
            headline: String::from(
                "Penguins win the Stanley Cup Championship!",
            ),
            location: String::from("Pittsburgh, PA, USA"),
            author: String::from("Iceburgh"),
            content: String::from(
                "The Pittsburgh Penguins once again are the best \
                 hockey team in the NHL.",
            ),
        }
    } else {
        SocialPost {
            username: String::from("horse_ebooks"),
            content: String::from(
                "of course, as you probably already know, people",
            ),
            reply: false,
            repost: false,
        }
    }
}
```

### Using Trait Bounds to Conditionally Implement Methods

By using a trait bound with an `impl` block that uses generic type parameters, we can implement methods conditionally for types that implement the specified traits.  
Here is an example.

```rust
use std::fmt::Display;

struct Pair<T> {
    x: T,
    y: T,
}

impl<T> Pair<T> {
    fn new(x: T, y: T) -> Self {
        Self { x, y }
    }
}

impl<T: Display + PartialOrd> Pair<T> {
    fn cmp_display(&self) {
        if self.x >= self.y {
            println!("The largest member is x = {}", self.x);
        } else {
            println!("The largest member is y = {}", self.y);
        }
    }
}
```

In this example, the `new` method is implemented for any types of `Pair<T>`.  
The `cmp_display` method, however, only implemented for types that have `Display` and `PartialOrd` traits.

We can also conditionally implement a trait for any type that implements another trait.   
Implementations of a trait on any type that satisfies the trait bounds are called *blanket implementations* and are used extensively in the Rust standard library.  
Here is an example.

```rust
impl<T: Display> ToString for T {
    // --snip--
}
```

## Validating References with Lifetimes

Lifetimes ensure that references are valid as long as we need them to be.  
Every reference in Rust has a lifetime, which is the scope for which that reference is valid.  
Most of the lifetime of reference is implicit and can be inferred by the compiler.  
However, sometimes the references may be used in some different ways which asks the lifetime to be different from the default setting.  
In this cases, we need to annotate the lifetime explicitly.

### Generic Lifetimes in Functions

Here is an example where the lifetimes annotation take effect.

```rust
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() { x } else { y }
}
```

The Rust compiler will throw an error, since it cannot determine the lifetime of the resultant reference, either from the `x` or `y`.  
To fix this error, we’ll add generic lifetime parameters that define the relationship between the references so that the borrow checker can perform its analysis.

### Lifetime Annotation Syntax

Lifetime annotations don’t change how long any of the references live.   
Rather, they describe the relationships of the lifetimes of multiple references to each other without affecting the lifetimes.

We use the apostrophe `'` to define the name of lifetime. We place the lifetime definition after the `&` of a reference, and before the reference's type.  
Here are some examples.

```rust
&i32        // a reference
&'a i32     // a reference with an explicit lifetime
&'a mut i32 // a mutable reference with an explicit lifetime
```

One lifetime annotation by itself doesn’t have much meaning, because the annotations are meant to tell Rust how generic lifetime parameters of multiple references relate to each other.

### In Function Signature

Just like the generic types, we need to declare the lifetime name inside angle brackets. Here is an example.

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

In this example, we want to express the constraint: the returned reference will be valid as long as the both of the parameters are valid.  
Note that the lifetime is just annotation. It will not change the lifetimes of any values passed in or returned.  
It tells the compiler should reject any values that violate the constraints.

Annotation of lifetime in functions only affect the functions' signature, not the function body.  
Like the types in the signature, the lifetime annotation also becomes a part of the function's contract.

### In Struct Definitions

We can define struct that hold reference rather than owned types.  
However, when using reference in struct, we need to annotate their lifetimes. Here is an example.

```rust
struct ImportantExcerpt<'a> {
    part: &'a str,
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().unwrap();
    let i = ImportantExcerpt {
        part: first_sentence,
    };
}
```

This annotation means an instance of `ImportantExcerpt` can’t outlive the reference it holds in its part field.

### Lifetime Elision

The following code can compiled successfully without lifetime annotation.

```rust
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}
```

This is because Rust's analysis these special patterns that the borrow checker could infer the lifetimes.  
They are called the *lifetime elision rules*.  
These rules don't provide full inference. If there is still ambiguity, we still need to resolve the error by adding the lifetime annotations.  

The compiler uses three rules to figure out the lifetimes of the reference where there aren't explicit annotation.

1. Assigning a lifetime parameter to each parameter that's a reference. For example `fn foo<'a, 'b>(x: &'a i32, y: &'i32) {}`.  
2. If there is only on input lifetime parameter, that lifetime is assigned to all output lifetime parameter. For example `fn foo<'a>(x: &'a i32) -> &'a i32`.  
3. If there are multiple input lifetime parameters, but one of them is `&self` or `&mut self` because this is a method, the lifetime of self is assigned to all output lifetime parameters.

### In Method Definitions

Lifetime names for struct fields always need to be declared after the `impl` keyword and then used after the struct’s name because those lifetimes are part of the struct’s type.  
Here is an example.

```rust
impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }
}
```

Because of the rule one, we don't need to add annotation before the `&self`.  
Here is an example of applying the rule three.

```rust
impl<'a> ImportantExcerpt<'a> {
    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention please: {announcement}");
        self.part
    }
}
```

### The Static Lifetime

The static lifetime `'static` is a special lifetime that the affected reference can live for the entire duration of the program.  
For example, the text of literal string is always available in the program's binary, so it can be annotate as follows: `let s: &'static str = "I have a static lifetime.";`

Sometimes, the compiler may suggest we use the `'static` lifetime in error message.  
However, we need to think about whether or not the reference you have actually lives the entire lifetime of your program, and whether you want it to.  
Most of the time it results from attempting to create a dangling reference or a mismatch of the available lifetimes.   
In such cases, the solution is to fix those problems, not to specify the `'static` lifetime.