
Compiling a single file: `rustc xxx.rs`， will produce an executable file.

## Managing Rust project with Cargo

### Creating the project

1. Create project `cargo new proj_name`
2. Enter into the project `cd proj_name`

This will create a folder with `Cargo.toml` as the configurating file, `.gitignore` as the git ignoring file and `src` as the source code folder.
There is a `main.rs` source code in the `src` folder, indicating that this project is for executable target. Otherwise there should be a `lib.rs` , indicating the this project is for library target.

In default, `cargo` uses the `git` as its version control system. To use another VCS or no VCS, using the flag `--vcs`.

### Compiling the project

Using `cargo build` to automatically build the rust project. Cargo will create a executable file at `target/debug/`. Or at `target/release/` with `--release` flag.  
Using `cargo run` to compile and run the program. Cargo will figure out whether the source code has been changed and need to be re-compiled.  
Using `cargo check` to check whether the project is compiled, but doesn't produce an executable. Used to check error. Faster than `cargo build`.