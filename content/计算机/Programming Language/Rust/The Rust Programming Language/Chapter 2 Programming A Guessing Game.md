# Chapter 2 Programming A Guessing Game

When there are dependencies, the `cargo build` will automatically fetch the dependent crate in `Cargo.toml`.  
It will create a `Cargo.lock` to memorize the version of each dependent crate in the first run.  
It is practical to include the `Cargo.lock` file in the source code control system.
For consistency and reproducibility, the cargo will use the same version in the following compiling, even there may be a new version uploaded.  
Using the `cargo update` command to update the crate.
