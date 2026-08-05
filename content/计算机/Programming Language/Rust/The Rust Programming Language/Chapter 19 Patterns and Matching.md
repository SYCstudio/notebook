# Chapter 19 Patterns and Matching

We use patterns to match against the structure of types in Rust.  
A pattern consists of some combination of : literals; destructured arrays, enums, structs, or tuples; variables; wildcards; placeholders.  
The components describe the shape of data. And the shape of data determine to run a particular piece of code.

## All the Places Patterns Can Be Used

**match arms**: all possibilities for the value in the match expression must be accounted for. The particular pattern `_` will match anything but never binds to a variable.

```rust
match x {
    None => None,
    Some(i) => Some(i + 1),
}
```

**let statements**

```rust
let (x, y, z) = (1, 2, 3);
```

**conditional if let expressions**: Compare to `match` expressions, this gives us more flexibility. Rust doesn’t require that the conditions in a series of `if let`, `else if`, and `else if let` arms relate to each other. `if let` can also introduce new variables that shadow existing variables in the same way that `match` arms can.

```rust
fn main() {
    let favorite_color: Option<&str> = None;
    let is_tuesday = false;
    let age: Result<u8, _> = "34".parse();

    if let Some(color) = favorite_color {
        println!("Using your favorite color, {color}, as the background");
    } else if is_tuesday {
        println!("Tuesday is green day!");
    } else if let Ok(age) = age {
        if age > 30 {
            println!("Using purple as the background color");
        } else {
            println!("Using orange as the background color");
        }
    } else {
        println!("Using blue as the background color");
    }
}
```

**while let conditional loops**: a while loop to run for as long as a pattern continues to match.

```rust
    let (tx, rx) = std::sync::mpsc::channel();
    std::thread::spawn(move || {
        for val in [1, 2, 3] {
            tx.send(val).unwrap();
        }
    });

    while let Ok(value) = rx.recv() {
        println!("{value}");
    }

```

**for loop**

```rust
    let v = vec!['a', 'b', 'c'];

    for (index, value) in v.iter().enumerate() {
        println!("{value} is at index {index}");
    }
```

**function parameters**

```rust
fn print_coordinates(&(x, y): &(i32, i32)) {
    println!("Current location: ({x}, {y})");
}

fn main() {
    let point = (3, 5);
    print_coordinates(&point);
}
```

## Refutability: Whether a Pattern Might Fail to Match

Patterns come in two forms: refutable and irrefutable.  
Patterns that will match for any possible value passed are *irrefutable*. For example `let x = 5`.    
Patterns that can fail to match for some possible value are *refutable*. For example `if let Some(x) = a_value`.

Function parameters, `let` statements, and `for` loops can only accept irrefutable patterns because the program cannot do anything meaningful when values don’t match.  
The `if let` and `while let` expressions and the `let...else` statement accept refutable and irrefutable patterns, but the compiler warns against irrefutable patterns because, by definition, they’re intended to handle possible failure.

We can use `let else` to handle possible failure.

```rust
    let Some(x) = some_option_value else {
        return;
    };
```

## Pattern Syntax

**matching literals**

```rust
    let x = 1;

    match x {
        1 => println!("one"),
        2 => println!("two"),
        3 => println!("three"),
        _ => println!("anything"),
    }
```

**matching named variables**  

`match`, `if let` and `while let` expressions start a new scope, which shadow the outside variables.  
For example, the following code will match the second arm, and the last `println!` will print the original y's value.

```rust
    let x = Some(5);
    let y = 10;

    match x {
        Some(50) => println!("Got 50"),
        Some(y) => println!("Matched, y = {y}"),
        _ => println!("Default case, x = {x:?}"),
    }

    println!("at the end: x = {x:?}, y = {y}");
```

**matching multiple patterns**

We can match multiple patterns using the `|` syntax in `match` expressions.

```rust
    let x = 1;

    match x {
        1 | 2 => println!("one or two"),
        3 => println!("three"),
        _ => println!("anything"),
    }

```

**matching ranges of values**

The `..=` syntax allows us to match to an inclusive range of values.  
Compiler will check that the range is not empty at compile time. For example, `5..=1` will be reject when used in match arms.  
Only `char` and numeric values in Rust can check whether is empty, so ranges are only allowed with numeric or `char` values.

```rust
    let x = 'c';

    match x {
        'a'..='j' => println!("early ASCII letter"),
        'k'..='z' => println!("late ASCII letter"),
        _ => println!("something else"),
    }
```

**destructuring to break apart values**

We can use the values that have the same name of fields of struct to assign to.

```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 0, y: 7 };

    let Point { x, y } = p;
    assert_eq!(0, x);
    assert_eq!(7, y);
}
```

We can also destructure with literal values as part of the struct pattern rather than creating variables for all the fields.

```rust
fn main() {
    let p = Point { x: 0, y: 7 };

    match p {
        Point { x, y: 0 } => println!("On the x axis at {x}"),
        Point { x: 0, y } => println!("On the y axis at {y}"),
        Point { x, y } => {
            println!("On neither axis: ({x}, {y})");
        }
    }
}
```

It is same for `Enum`.

```rust
enum Color {
    Rgb(i32, i32, i32),
    Hsv(i32, i32, i32),
}

enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(Color),
}

fn main() {
    let msg = Message::ChangeColor(Color::Hsv(0, 160, 255));

    match msg {
        Message::ChangeColor(Color::Rgb(r, g, b)) => {
            println!("Change color to red {r}, green {g}, and blue {b}");
        }
        Message::ChangeColor(Color::Hsv(h, s, v)) => {
            println!("Change color to hue {h}, saturation {s}, value {v}");
        }
        _ => (),
    }
}
```

We can use `_` as a wildcard pattern that will match any value but not bind to the value.  

```rust
fn foo(_: i32, y: i32) {
    println!("This code only uses the y parameter: {y}");
}

fn main() {
    foo(3, 4);
}
```

We can use `_` inside another pattern to ignore just part of a value.

```rust
    let mut setting_value = Some(5);
    let new_setting_value = Some(10);

    match (setting_value, new_setting_value) {
        (Some(_), Some(_)) => {
            println!("Can't overwrite an existing customized value");
        }
        _ => {
            setting_value = new_setting_value;
        }
    }

    println!("setting is {setting_value:?}");
```

Starting a variable's name with `_` can tell Rust not to warn about the unused variable.  
Note that `_x` still binds the value to the variables, whereas `_` doesn't bind at all.

With values that have many parts, we can use the `..` syntax to use specific parts and ignore the rest, avoiding the need to list underscores for each ignored value.  
The `..` pattern ignores any parts of a value that we haven’t explicitly matched in the rest of the pattern.  
The `..` will expand to as many values as it needs to be. However, it must be unambiguous.

```rust
fn main() {
    let numbers = (2, 4, 8, 16, 32);

    match numbers {
        (first, .., last) => {
            println!("Some numbers: {first}, {last}");
        }
        //(.., second, ..) is not allowed
    }
}
```

### Adding Conditionals with Match Guards

A *match guard* is an additional `if` condition, specified after the pattern in a `match` arm, that must also match for that arm to be chosen.  
They are only available in `match` expressions.

```rust
    let num = Some(4);

    match num {
        Some(x) if x % 2 == 0 => println!("The number {x} is even"),
        Some(x) => println!("The number {x} is odd"),
        None => (),
    }
```

The downside of match guard is that the compiler doesn't try to check for exhaustiveness.  

We can use match guard to solve our pattern-shadowing problem.

```rust
fn main() {
    let x = Some(5);
    let y = 10;

    match x {
        Some(50) => println!("Got 50"),
        Some(n) if n == y => println!("Matched, n = {n}"),
        _ => println!("Default case, x = {x:?}"),
    }

    println!("at the end: x = {x:?}, y = {y}");
}
```

We can also use the `|` operator in a match guard to specify multiple patterns.  
The match guard condition will apply to all the patterns.

```rust
    let x = 4;
    let y = false;

    match x {
        4 | 5 | 6 if y => println!("yes"), // note that the condition is apply to 4, 5, 6, not only apply to 6
        _ => println!("no"),
    }
```

### Using `@` bindings

We can use the *at* operator `@` to bind a variable that holds a value at the same time we're testing that value.  

```rust
    enum Message {
        Hello { id: i32 },
    }

    let msg = Message::Hello { id: 5 };

    match msg {
        Message::Hello { id: id @ 3..=7 } => {
            println!("Found an id in range: {id}")
        }
        Message::Hello { id: 10..=12 } => {
            println!("Found an id in another range")
        }
        Message::Hello { id } => println!("Found some other id: {id}"),
    }
```

In the above example, we can use the `id` in the first and the third arms, but not the second arms.
