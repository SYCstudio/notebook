# Chapter 14 More About Cargo and Crates.io

## Customizing Builds with Release Profiles

In default, Cargo has two main profiles: `dev` profile with `cargo build`, and `release` profile with `cargo build --release`.  
These are the default settings for us when we do not explicitly add any `[profile.*]` section in project's `cargo.toml`.

```toml
[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
```

We can write any values to overwrite the default settings.  
The all possible settings can be found in https://doc.rust-lang.org/cargo/reference/profiles.html

## Making Useful Documentation Comments

In Rust, we can use `///` to start a section of comments that can be used to generate documents.  
It support Markdown notation. By running `cargo doc`, we can generate HTML-based document in the `target/doc` directory. Or the `cargo doc --open` to build the document and open it in a web browser.

The documentation is used for another users to know how to *use* your API, not how it *implemented*.  
Normally, we are recommended to have `Examples`, `Panics` , `Errors`, and `Safety` sections in the documentation.

Additionally, we can run `cargo test` to test the examples in the documentation comments. Here is an example.

```rust
/// Adds one to the number given.
///
/// # Examples
///
/// ```
/// let arg = 5;
/// let answer = my_crate::add_one(arg);
///
/// assert_eq!(6, answer);
/// ```
pub fn add_one(x: i32) -> i32 {
    x + 1
}
```

> This feature support the `///`, `/* */`, and crate-level comments `//! crate docs`.  
> Using the `should_panic(expected="")` keyword to annotate that is should panic, with optional `expectecd` argument.  
> Using the `compile_fail` keyword to annotate that is should not pass the compilation.  
> Using the `no_run` keyword to annotate that is should pass the compilation but do nor run.  
> Using the `ignore` keyword to skip it.  

If we want to completely close the `doctest` feature, we can put the following in `Cargo.toml`.

```toml
[lib]
doctest = false
```

The style of doc comment `//!` adds documentation to the item that *contains* the comments rather than to the items *following* the comments.  
We usually use this feature to document the `crate`.

## Cargo Workspace

Rust offers the `workspace` feature that can help with managing multiple related packages that are developed in tandem.  
A workspace is a set of packages that share the same `Cargo.lock` and output directory.

#### Creating a Workspace

To create a workspace, we need to place a `Cargo.toml` in a folder with no `[package]` section but `[workspace]` section. Here is an example.

```toml
[workspace]
resolver = "3" # this number guide us to use which version of Cargo's resolver algorithm in our workspace
```

Then we can use `cargo new xxx` to add binary or `cargo new xxx --lib` to add library. These members will automatically added to the root `Cargo.toml`, and create their own sub folder.  
All the sub crate will share a common `target` folder in the root. Here is an example.

```plain
├── Cargo.lock
├── Cargo.toml
├── add_one
│   ├── Cargo.toml
│   └── src
│       └── lib.rs
├── adder
│   ├── Cargo.toml
│   └── src
│       └── main.rs
└── target
```

#### Dependencies

To let a inner crate use another crate, we need to add path in its `Cargo.toml` file. Cargo doesn't assume that crates in a workspace will depend on each other.  
For example, in the above scenario, we can add the following text in `adder`'s `Cargo.toml` file to make it depend on `add_one` library.

```toml
[dependencies]
add_one = { path = "../add_one" }
```

We can use the `-p` argument to specify which package in the workspace we want to run in `cargo run -p <name>`.

We can also put external dependencies in the `dependencies` sections as well.  
If two or more crates depend on the same external dependencies, Cargo will ensure that they use the same version.  
If crates in the workspace specify incompatible versions of the same dependency, Cargo will resolve each of them but will still try to resolve as few versions as possible.

#### Running Tests in Workspace

The command `cargo test` will collect and run all the tests in sub crates.  
Or we can add `-p` argument to specifically run test in one crate.
