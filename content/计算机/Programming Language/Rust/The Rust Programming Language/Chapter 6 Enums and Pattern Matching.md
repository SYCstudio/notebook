# Chapter 6 Enums and Pattern Matching

## Defining an Enum
Enum gives a way to say a value is one of a possible set of values. Here is an example of defining enums.

```rust
enum IpAddrKind {
	V4,
	V6,
}

let four = IpAddrKind::V4;
let six = IpAddrKind::V6;
```

Rust allows us to put data directly into enums. The name of each enum variant also becomes a function which can construct an instance of the enum.

```rust
enum IpAddr {
	V4(String), 
	V6(String),
} 
let home = IpAddr::V4(String::from("127.0.0.1"));
let loopback = IpAddr::V6(String::from("::1"));
```

Moreover, each variant can have different types.

```rust
enum IpAddr {
	V4(u8, u8, u8, u8), 
	V6(String),
}
let home = IpAddr::V4(127, 0, 0, 1);
let loopback = IpAddr::V6(String::from("::1"));
```

Like struct, `enum` also support the `impl` block. We can define methods associated with enums.

### The Option Enum

`Option` type is a common enum used in Rust. It is defined as follow:

```rust
enum Option<T> {
	None, Some(T),
}
```

## The `match` Control Flow Construct

`match` allows us to compare a value against a series of patterns and execute code based on which pattern matches.  
In Rust, values go through each pattern in a `match`. It will execute the code associated with the first pattern it fits.

```rust
enum Coin {
	Penny, Nickel, Dime, Quarter,
}
fn value_in_cents(coin: Coin) -> u8 {
	match coin {
		Coin::Penny => 1, 
		Coin::Nickel => 5, 
		Coin::Dime => 10, 
		Coin::Quarter => 25, 
	}
}
```

We call them match arms. Each arm has two part: a pattern and some code.  
The code associated with each arm is an expression.

We can use match to extract values out of enum variants. Here is an example using the `Option<T>`.

```rust
fn plus_one(x: Option<i32>) -> Option<i32> {
	match x {
		None => None,
		Some(i) => Some(i + 1),
	}
}
```

The match pattern in Rust is exhaustive. That is, the arms' patterns must cover all possibilities.  
If we want to add a default arm, use `other` or `_` for special pattern.

```rust
// when we need the value
let dice_roll = 9;
match dice_roll {
	3 => add_fancy_hat(),
	7 => remove_fancy_hat(),
	other => move_player(other),
}

// when we don't need the value
let dice_roll = 9;
match dice_roll {
	3 => add_fancy_hat(),
	7 => remove_fancy_hat(), 
	_ => reroll(),
}
```

## Concise Control Flow with `if let`

The `if let` syntax allows us to combine `if` and `let` into a less verbose way, when handling values that match one pattern while ignoring the rest.  
In the following example, the two programs are equivalent.

```rust
// using match
let config_max = Some(3u8);
match config_max { 
	Some(max) => println!("The maximum is configured to be {max}"),
	_ => (),
}

// using if let
let config_max = Some(3u8);
if let Some(max) = config_max { 
	println!("The maximum is configured to be {max}");
}
```

We can add an `else` block for `if let`. In this case, it will works same as the block that go with the `_` case in `match`.

Similar, we have `let else` syntax to simplify the following situation.

```rust
// complicated way
fn describe_state_quarter(coin: Coin) -> Option<String> {
	let state = if let Coin::Quarter(state) = coin {
		state
	} else { 
		return None; 
	};
	if state.existed_in(1900) { 
		Some(format!("{state:?} is pretty old, for America!"))
	} else { 
		Some(format!("{state:?} is relatively new.")) 
	}
}

// using let return to simplify
fn describe_state_quarter(coin: Coin) -> Option<String> {
	let Coin::Quarter(state) = coin else { 
		return None; 
	}; 
	if state.existed_in(1900) {
		Some(format!("{state:?} is pretty old, for America!")) 
	} else {
		Some(format!("{state:?} is relatively new.")) 
	}
}
```

We call it `staying on the happy path`, since we focus handling the positive situation in the main function body. The `none` branch return earlier.
