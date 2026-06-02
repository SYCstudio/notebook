# Chapter 7 Packages, Crates, and Modules

The Rust module system:

* **Packages** A Cargo feature that lets you build, test, and share crates   
* **Crates** A tree of modules that produces a library or executable    
* **Modules and use** Let you control the organization, scope, and privacy of paths   
* **Paths** A way of naming an item, such as a struct, function, or module

## Packages and Crates

*crate* is the smallest amount of code that Rust compiler considers at a time.  
For example, when we use the `rustc` to compile a single file, that single file is a *crate*.  

A crate can have two form:

* *Binary crates*: executable program. Must have a function called `main`.  
* *Library crates*: non-executable, providing functionality for other programs or libs.

In most cases, when we say "crate", we mean the library crate.  
The `crate root` is a source file that the Rust compiler starts from and makes up the root module of your crate.

A *package* is a bundle of one or more crates that provides a set of functionality.  
A package is always having a `cargo.toml` file which describe how to build those crates.  
A package can contain as many binary crates as you like, but at most only one library crate.

By default, Cargo follows a convention that `src/main.rs` is the crate root of a binary crate with the same name as the package.  
Likewise, the `src/lib.rs` is the crate root of the library.  
If a package contains both `src/main.rs` and `src/lib.rs`, it has two crates: a binary and a library, both with the same name as the package.  
A package can have multiple binary crates by placing files in the `src/bin` directory: Each file will be a separate binary crate.

## Control Scope and Privacy with Modules

*Modules* let us organize code within a crate for readability and easy reuse.  
It also allows us to control the privacy. Code within a module is private by default.  
We use the keyword `mod` to define a module. Here is an example.

```rust
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}
        fn seat_at_table() {}
    }
    mod serving {
        fn take_order() {}
        fn serve_order() {}
        fn take_payment() {}
    }
}
```

The `src/main.rs` or `src/lib.rs` are called `crate root`. Either of these two files form a module named `crate` at the root.  
Here is the module tree of the above example.

```plain
crate
 └── front_of_house
     ├── hosting
     │   ├── add_to_waitlist
     │   └── seat_at_table
     └── serving
         ├── take_order
         ├── serve_order
         └── take_payment
```

## Paths for Referring to an Item in the Module Tree

Rust uses `path` to find an item in the module tree. There are two forms of path:

* Absolute path: a full path start from a crate root. For external crate, it begins with the crate name; for the current crate, it begins with the literal `crate`.  
* Relative path: starts from the current module. Using `self`, `super` or an identifier in the current module.

Both the absolute path and relative path uses the double colons `::` to separate the identifiers.

In Rust, all items (functions, methods, structs, enums, modules, and constants) are private to parent modules by default.  
Items in a parent module can’t use the private items inside child modules, but items in child modules can use the items in their ancestor modules.  
We can use the `pub` keyword to make a item public.  
The pub keyword on a module only lets code in its ancestor modules refer to it, not access its inner code. Here is an example.

```rust
// compile error !
mod front_of_house {
    pub mod hosting {
        fn add_to_waitlist() {}
    }
}
pub fn eat_at_restaurant() {
    // Absolute path
    crate::front_of_house::hosting::add_to_waitlist();  //can't compile

    // Relative path
    front_of_house::hosting::add_to_waitlist();  // can't compile
}

// compile ok
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}
// -- snip --
```

> Best Practice for packages with a binary and a library:  
> the binary have just enough code to start an executable; the library contains all the public API.   
> The binary calls code defined in the library crate.  
> We define the module tree in `src/lib.rs`. The binary crate becomes a user of the library crate. It also helps to design a good API.

Using *super* allows us to reference an item that we know is in the parent module.

### Making Structs and Enums public

We can also use the `pub` keyword to make structs or enums public.  
If we use pub before a struct definition, we make the struct public, but the fields of the struct is still private.  
This allows us to choose whether to public case by case. Here is an example.

```rust
mod back_of_house {
    pub struct Breakfast {
        pub toast: String,                  // this is public
        seasonal_fruit: String,             // this is private
    }

    impl Breakfast {
        pub fn summer(toast: &str) -> Breakfast {
            Breakfast {
                toast: String::from(toast),
                seasonal_fruit: String::from("peaches"),
            }
        }
    }
}

pub fn eat_at_restaurant() {
    // Order a breakfast in the summer with Rye toast.
    let mut meal = back_of_house::Breakfast::summer("Rye");
    // Change our mind about what bread we'd like.
    meal.toast = String::from("Wheat");
    println!("I'd like {} toast please", meal.toast);

    // The next line won't compile if we uncomment it; we're not allowed
    // to see or modify the seasonal fruit that comes with the meal.
    // meal.seasonal_fruit = String::from("blueberries");
}
```

In contrast, if we make an enum public, all of its variants are then public.

## Bringing Paths into Scope with the `use` Keyword

We can create a shortcut to a path with the use keyword once and then use the shorter name everywhere else in the scope.  
The above example can be rewrite as the following.

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}
```

Note that use only creates the shortcut for the particular scope in which the use occurs.  
In the above example, if we move the `eat_at_restaurant` into a new module, it won't compile correctly.

### Creating Idiomatic use Paths

Bringing the function’s parent module into scope with `use` means we have to specify the parent module when calling the function.   
Specifying the parent module when calling the function makes it clear that the function isn’t locally defined while still minimizing repetition of the full path.  
In the above example, we don't recommend `use crate::front_of_house::hosting::add_to_waitlist;` even though it will compile well.  
On the other hand, when bringing in structs, enums, and other items with use, it’s idiomatic to specify the full path.  
For example, `use std::collections::HashMap;`

We can specific a local name, or *alias* after the `use` path by `as` for the type.  
For example, `use std::io::Result as IoResult;`

We can re-exporting a name by using `pub use`. This enables the code outside that scope to refer to that name as if the name is defined in that scope.

When import multiple names from the same external crate, writing their path one by one will take much of the space.  
Rust allows us to use a nested way to bring the same items into scope in one line. Here is an example

```rust
use std::cmp::Ordering;
use std::io;
// same as
use std::{cmp::Ordering, io};

use std::io;
use std::io::Write;
// same as
use std::io::{self, Write};
```

If we want to bring all the public items defined in a path into current scope, we can use the `*` glob operator after the path.  
For example `use std::collections::*;` brings all the public items in `std::collections::` into current scope.  
The glob operator is often used when testing to bring everything into the `tests` module.

## Separating Modules into Different Files

When the code files get larger, we want to separate the code into several files.  
Usually, we leave the definition in the `src/lib.rs` (or `src/main.rs`). Use the `mod` keyword to let the compiler know there is a sub-module.  
Note that, the `mod` introduces the file into the project, and we only need to place it once in the module tree (unlike `include` in some other languages). Other part of the project can use the path to refer it.  
