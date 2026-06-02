# Chapter 9 Error Handling

Rust asks you to acknowledge the possibility of an error and take some actions.  
The errors are grouped into two categories: recoverable errors and unrecoverable errors.

## Unrecoverable Errors with `panic!` Macro

There are two ways to cause a panic: taking an action that cause the code to panic (for example, accessing an array past the end) or explicitly calling the `panic!` macro.    
By default, a panic will print a message, unwind, clean up the stack, and quit.  
We can let the Rust display the call stack when a panic occur by setting the environment variable (`RUST_BACKTRACE=1`).  
The *backtrace* is a list of all the functions that have been called to get to this point. 

> Unwinding the stack or aborting:  
> The default action of waking back up the stack and cleaning up the data from each function of panic need a lot of work, which take a a lot of place in the resultant binary.  
> Rust allows you to aborting immediately, by setting the `panic = 'abort'` in the `[profile]` section (for example, in the `profile.release` means setting in the release mode) in `Cargo.toml` file.  
> This will let the operating system handle the clean up work.


## Recoverable Errors with `Result`

`Result` is for errors that are not serious enough to quit the program, and we can easily interpret and respond to them.  
The `Result` is defined as having two variants: `Ok` and `Err`, as follows.

```rust
enum Result<T, E> {
	Ok(T),
	Err(E),
}
```

Here is an example of using the `Result` as the resultant value of opening a file.

```rust
use std::fs::File;
use std::io::ErrorKind;

fn main() {
    let greeting_file_result = File::open("hello.txt");

    let greeting_file = match greeting_file_result {
        Ok(file) => file,
        Err(error) => match error.kind() {
            ErrorKind::NotFound => match File::create("hello.txt") {
                Ok(fc) => fc,
                Err(e) => panic!("Problem creating the file: {e:?}"),
            },
            _ => {
                panic!("Problem opening the file: {error:?}");
            }
        },
    };
}
```

We can use the closures to make the code more concise. Here is the alternative way to write the same logic.

```rust
use std::fs::File;
use std::io::ErrorKind;

fn main() {
    let greeting_file = File::open("hello.txt").unwrap_or_else(|error| {
        if error.kind() == ErrorKind::NotFound {
            File::create("hello.txt").unwrap_or_else(|error| {
                panic!("Problem creating the file: {error:?}");
            })
        } else {
            panic!("Problem opening the file: {error:?}");
        }
    });
}
```

### Shortcuts for Panic or Error

The `Result<T, E>` provides many helper functions to do various, more specific tasks.  
`unwrap` will return the value inside the `Ok` if the `Result` Value is the `Ok`  variant, otherwise will call the `panic!` macro and quit the program.  
`expect` works similarity but lets us choose the `panic!` error message

### Propagating Errors

Instead of handling the error within the function in place, we can return the error to the calling code and let it decide what to do.  
Here is an example.

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let username_file_result = File::open("hello.txt");

    let mut username_file = match username_file_result {
        Ok(file) => file,
        Err(e) => return Err(e),
    };

    let mut username = String::new();

    match username_file.read_to_string(&mut username) {
        Ok(_) => Ok(username),
        Err(e) => Err(e),
    }
}
```

Rust provides a `?` operator shortcut for the same functionality. Here is the function that behavior the same but its implementation uses the `?` operator.

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let mut username_file = File::open("hello.txt")?;
    let mut username = String::new();
    username_file.read_to_string(&mut username)?;
    Ok(username)
}
```

If the value of the `Result` before the `?` operator is `Ok` variant, the expression will return the value inside the `Ok`. And the program will continue.  
Otherwise, it will return the whole function and propagate the `Error` to the calling code.  
`Error` values that have the `?` operator called on them go through the `from` function, defined in the `From` trait in the standard library, which is used to convert values from one type into another.  
That `from` trait will convert the type from the type received to the error type that defined in the return type of the current function.

We can further chaining the method to make the program more concise.

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let mut username = String::new();

    File::open("hello.txt")?.read_to_string(&mut username)?;

    Ok(username)
}

```

The `?` operator can be used with `Option<T>` as well.  
The function is similar: if the value is `None`, it will return `None` immediately from the function; otherwise it will emit the value inside the `Some`.  

The `?` cannot mix using the `Result<T, E>` and `Option<T>`. The type must match the resultant of the function.  
The compiler will not do the converting automatically. But we can use methods like the `ok` method on `Result` or the `ok_or` method on `Option` to do the conversion explicitly.

## To `panic!` or Not to `panic!`

We choose to `panic!` for any error situation.  
We give the calling code options when we choose to use the `Result<T, E>`.

In situations such as examples, prototype code, and tests, it’s more appropriate to write code that panics instead of returning a Result.
