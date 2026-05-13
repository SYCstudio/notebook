## Variables and Mutability
In Rust, variables are immutable by default.  
Using the `mut` explicitly to make a variable mutable.

### Constant

Using the `const` to declare a constant. Constants are always immutable. And the type of the constant must be annotated.  
It can be declared in any scope, including the global scope.  
The value of a constant must can be determined at compile time.

### Shadowing

Shadowing allows programmer to declare the a new variable with the same name as a previous variable. In that case, we say that the first variable is *shadowed* by the second.  
Here is an example of shadowing and scope.

```rust
fn main() {
	let x = 5;
	let x = x + 1; 
	{ 
		let x = x * 2; 
		println!("The value of x in the inner scope is: {x}"); // x = 12
	} 
	println!("The value of x is: {x}"); // x = 6
} 
```

Comparing to `mut`, shadowing still keeps the variable immutable. It use `let` to perform limited transformation among variable but have them immutable after the transformation have completed.  
Moreover, it allows us to change the type of the value but reuse the same name.

## Data Types

Rust is a statically typed language. The types of all the variables must be known at compile time.  
We look into two classes of types, scalar types and compound types.

### Scalar Types

A scalar type represent a single value. There four primary scalar types in Rust: integers, float-point numbers, Booleans and characters.

![[Integer_types.png]]