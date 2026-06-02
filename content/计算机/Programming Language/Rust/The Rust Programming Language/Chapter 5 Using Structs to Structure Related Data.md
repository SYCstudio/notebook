# Chapter 5 Using Structs to Structure Related Data


Structs allows us to package and name multiple related values into a meaningful group.

## Defining and Instantiating Structs

We use `struct` keyword to define a struct. Here is an example.

```rust
struct User {
	active: bool, 
	username: String, 
	email: String, 
	sign_in_count: u64,
}
```

By specifying concrete values for each of the fields, we can instantiate a struct. Rust allows the order of instantiating and defining can be different.

```rust
fn main() {
	let user1 = User {
		active: true, 
		username: String::from("someusername123"), 
		email: String::from("someone@example.com"), 
		sign_in_count: 1, 
	}; 
}
```

Like the variable, the instance of structs are immutable by default. Using the `mut` keyword to make it mutable.  
If a struct is marked mutable, the entire instance is mutable. Rust doesn't allow us to mark only certain fields as mutable.

### Special Syntax

The syntax of `field init shorthand` allows us to match the same name of parameter and field when initializing structs. Here is an example of the above `User` struct.

```rust
fn build_user(email: String, username: String) -> User {
	User {
		active: true,
		username, // rather than 'username: username'
		email,
		sign_in_count: 1,
	}
}
```

The syntax of `struct update` allows us to create new struct that similar to an old struct easier. Here is an example.  
Note that this syntax's behavior is like the `=` assignment. That is, the data is moved. 

```rust
let user2 = User {
	email: String::from("another@example.com"), 
	..user1 // make other field of user2 same as user1
};
```

### Tuple Structs

`tuple structs` are similar to tuples. They have struct name but no field name.  
It is useful when we want to give a whole tuple a name and make it a different type.  
Note that, even if two tuple structs have exact the same inner types, they are different.   
Like tuple, it allows you to deconstruct them into individual pieces, but need to name the type.  
Here is an example. The `Color` and `Point` are different types.

```rust
struct Color(i32, i32, i32);
struct Point(i32, i32, i32);
fn main() {
	let black = Color(0, 0, 0);
	let origin = Point(0, 0, 0);
	let Point(x, y, z) = origin;
}
```

### Unit-like Structs

`unit-like` structs are structs that don't have any field. They behave similar to `()`, the unit type.  
It can be useful when you need to implement a trait on some type but don’t have any data that you want to store in the type itself.  
Here is an example.

```rust
struct AlwaysEqual;
fn main() {
	let subject = AlwaysEqual;
}
```

## Methods
 
 `Method` are similar to functions. However, a method is always related to a struct (or `enum`, `trait object`).  
 Their first parameter is always `self`, which represents the instance of the struct the method is being called on.  
 Here is an example showing the syntax of methods.

```rust
#[derive(Debug)]
struct Rectangle {
	width: u32, height: u32,
}
impl Rectangle {
	fn area(&self) -> u32 {  // '&self' is actually short for 'self: &Self'
		self.width * self.height
	}
}
fn main() {
	let rect1 = Rectangle {  width: 30, height: 50, };
	println!(
		"The area of the rectangle is {} square pixels.",
		rect1.area()
	);
}
```

If we want to change the value, we need to use the `&mut self`.  
Having a method that takes ownership of the instance by using just `self` as the first parameter is rare; this technique is usually used when the method transforms self into something else and you want to prevent the caller from using the original instance after the transformation.

Rust allows a method use the same name with a field in struct.

### Associated Functions

Functions defined in `impl` blocks are called associated functions.  
We can define associated function with the first parameter is not `self`. These functions are usually used for constructors.