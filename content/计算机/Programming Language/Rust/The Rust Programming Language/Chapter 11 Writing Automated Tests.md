# Chapter 11 Writing Automated Tests

In this chapter, we discuss the mechanics of Rust's testing facilities.

## How to Write Tests

The body of test functions usually have three components:

1. Set up any needed data or state.  
2. Run the code we want to test.  
3. Check the results are what we expect.

### Structuring Test Functions

We can add an attribute `#[test]` on the line before the `fn` to change a function into a test function.  
Then we can run the tests with the `cargo test` command.   
Rust will build the testing binary that run the annotated functions and report whether each of the test functions passes or fails.  
Here is an example

```rust
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

In the above example, `#[cfg(test)]` marks the module only compiled in `cargo test`.  
Note that we can also have non-testing function in the `tests` module, for example, helping to setup scenarios.

### Checking Result with `assert!`, `assert_eq!` and `assert_ne!` macros

We can use `assert!` macro to ensure that some conditions in a test evaluates to `true`.  

We can use `assert_eq!` and `assert_ne!` macros to test equality. They also print the two values if the assertation fails.  
Under the surface, these two macros uses the operator `==` and `!=` respectively. So the value been compared must implement the `PartialEq` and `Debug` traits.  
We can put additional message to these macros, after the default parameters.  

### Checking for Panics with `should_panic` attribute

We can add `should_panic` attribute to check whether our code can handle the error well. Here is an example.

```rust
pub struct Guess {
    value: i32,
}

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 || value > 100 {
            panic!("Guess value must be between 1 and 100, got {value}.");
        }

        Guess { value }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic]
    fn greater_than_100() {
        Guess::new(200);
    }
}
```

We can add an optional `expect` parameter to make the `should_panic` more precise.  
The test harness will make sure that the failure message contains the provided text.  
For the above example, we can rewrite it as the follows to better match the panic result.

```rust
// --snip--

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!(
                "Guess value must be greater than or equal to 1, got {value}."
            );
        } else if value > 100 {
            panic!(
                "Guess value must be less than or equal to 100, got {value}."
            );
        }

        Guess { value }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "less than or equal to 100")]
    fn greater_than_100() {
        Guess::new(200);
    }
}
```

### Using `Result<T, E>` in Tests

We can also use `Result<T, E>` rather than just panic in tests.  
Here is an example.

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() -> Result<(), String> {
        let result = add(2, 2);

        if result == 4 {
            Ok(())
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }
}
```

These allow us to use the question mark `?` in the testing function body, which can be convenient to test the function that return `Result`.  
However, we cannot use the `Result<T, E>` as result with the `[should_panic]` attribute simultaneously.  
In this case, we can use the `assert!(result.is_err())` to check the error is indeed happened, rather than use the `should_panic` attribute.

## Controlling How Tests Are Run

The default behavior of `cargo test` is to run all the tests in parallel and capture the output.  
We can change this behavior by specifying command line options.

Some command line options go to `cargo test`, and some go to the resultant test binary.   
To separate these two types of arguments, you list the arguments that go to `cargo test` followed by the separator `--` and then the ones that go to the test binary.

### Running Tests in Parallel or Consecutively

The tests run at parallel by default. So we need to ensure that tests don't depend on each other or any shared state.  
We can use the `--test-thread` to control its concurrency. For example 

```
$ cargo test -- --test-threads=1
```

### Showing Function Output

Rust testing will capture all the standard output (for example `println!`) and only print them when the cases fail.  
We can use the `--show-output` to see printed values for passing tests as well.

### Running a Subset of Tests by Name

We can choose which tests to run by passing `cargo test` the name or names of the test(s) we want to run as an argument.  
We can specify a full name, or part of a test name. Any test whose name matches the value will be run.  
Also note that the module in which a test appears becomes part of the test’s name, so we can run all the tests in a module by filtering on the module’s name.

### Ignoring Tests Unless Specifically Requested

We can add `#[ignore]` attribute after the `#[test]` to mark a testing function ignored.  
It will be ignored when we run `cargo test`.  
If we want to run only the ignored tests, we can use `cargo test -- --ignored`.  
If you want to run all tests whether they’re ignored or not, you can run `cargo test -- --include-ignored`.

## Test Organization

*Unit tests* are small and more focused, testing one module in isolation at a time, and can test private interfaces.   
*Integration* tests are entirely external to your library and use your code in the same way any other external code would, using only the public interface and potentially exercising multiple modules per test.

### Unit Tests

We can put unit tests in the `src` directory in each file with the code that they’re testing.   
The convention is to create a module named `tests` in each file to contain the test functions and to annotate the module with `cfg(test)`.  
The `cfg(test)` attribute ensure that this part of the code will not included in the `cargo build` processing to save the compiling time and little binary result.

#### Private Function Tests

Rust allows to test private function. Here is an example. Note that the `internal_adder` is a private function.

```rust
pub fn add_two(a: u64) -> u64 {
    internal_adder(a, 2)
}

fn internal_adder(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn internal() {
        let result = internal_adder(2, 2);
        assert_eq!(result, 4);
    }
}
```

In the community, whether to test private function directly has been a long term debate. Some languages just don't allow it.  
Rust just provides the mechanics. It is the developer's responsibility to decide whether to use it or not.

### Integration Tests

Rust's integration tests are entirely external to the library.  
Usually, we create a `tests` folder at the top level, next to `src`.  
Cargo will know to look for integration tests in this folder, and compile each of them as an individual crate.  
Note that we don't need the annotation `#[cfg(test)]` because Cargo will treat the `tests` folder specially.

The `cargo test` will start three tests: unit tests, integration tests and docs tests. If any test in a section fails, the following sections will not be run.  
If we want to run a specific integration tests, we can use `cargo test --test <filename>`.

#### Submodules in Integration Tests

As mentioned earlier, each file in the tests directory is compiled as its own separate crate.  
So if we want to set helper functions for tests, we can not just put a `common.rs` code file in the `tests` folders. It will be treated as a testing file.  
Instead, we need to use the old Rust naming convention, that is `tests/common/mod.rs` to put these functionalities. Then use `mod common` at each testing file.

#### Integration Tests for Binary Crates

If our project is a binary crate that only contains `main.rs` not `lib.rs`, we cannot create integration tests in the `tests` directory.  
We cannot bring the functions from `main.rs` into scope with a `use` statement.  

