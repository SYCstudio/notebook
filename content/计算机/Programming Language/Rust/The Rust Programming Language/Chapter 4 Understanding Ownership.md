# Chapter 4 Understanding Ownership

## Ownership

In Rust, memory is managed through a system of ownership with a set of rules that the compiler checks. If any of the rules are violated, the program won’t compile.

### Ownership Rules

Ownership rules:

1. Each value in Rust has an owner.  
2. There can only be one owner at a time.  
3. When the owner goes out of scope, the value will be dropped.

### Variable Scope

A *scope* is the range within a program for which an item is valid.

### The String Type

String type manages data allocated on heap (compare to string literal).  
It is able to store amount of text which is unknown at compile time.  
It can be mutated (the string literal cannot).

### Memory and Allocation

In Rust, the memory is automatically returned once when the variable is out of scope.

Rust uses *move* rather than *shallow copy* or *deep copy* when apply assignment on variable that allocated on heap. Here is an example.

```rust
let s1 = String::from("hello");
let s2 = s1; // the s1 is moved to s2, s1 is invalid.
println!("{s1}, world!"); // compile error! borrow of moved value `s1`
```

Rust will never automatically create **deep** copies of you data.

### Cloning Data

Using the `clone` method when we *do* want to deeply copy the data on heap.

```rust
let s1 = String::from("hello");
let s2 = s1.clone();
println!("s1: {s2}, s2: {s2}");
```

Rust has a special annotation: the *Copy* trait. We can place on types are stored on the stack (like integer).  
If a type implement the copy trait, variable that use it do not move, but rather are trivially copied, making them still valid after assignment to another  variable.  
The Copy trait and Drop trait (which control the memory free) is contradicted. Rust doesn't allow them to be implemented on the same type.

### Ownership and Functions

Passing a variable to a function is similar to assigning a value to a variable. The variable will be moved or copied, depending on the types.

```rust
fn main() {
	let s = String::from("hello"); // s comes into scope 
	takes_ownership(s); // s's value moves into the function...  
						// ... and so is no longer valid here 
	let x = 5; // x comes into scope 
	makes_copy(x);  // because i32 implements the Copy trait,  
					// x does NOT move into the function, 
					// so it's okay to use x afterward
}
```

### Return Values and Scope

Returning values can also transfer ownership.

```rust
fn main() {
	let s1 = gives_ownership(); // gives_ownership moves its return value into s1 
	let s2 = String::from("hello"); // s2 comes into scope 
	let s3 = takes_and_gives_back(s2); // s2 is moved into takes_and_gives_back, which also moves its return value into s3 
} // Here, s3 goes out of scope and is dropped. s2 was moved, so nothing happens. s1 goes out of scope and is dropped. 
fn gives_ownership() -> String { // gives_ownership will move its return value into the function that calls it 
	let some_string = String::from("yours"); // some_string comes into scope 
	some_string // some_string is returned and moves out to the calling function 
}  // this function takes a String and returns a String 
fn takes_and_gives_back(a_string: String) -> String { // a_string comes into scope
	a_string // a_string is returned and moves out to the calling function
}
```

They all follow the same pattern:  

1. Assigning a value to another variable moves it.
2. When a variable that includes data on the heap goes out of the scope, the value will be cleaned up by drop unless the ownership is transferred to another variable.

## Reference and Borrowing

A reference is like a pointer (in that it's an address we can follow) to access a data. The data is owned by another variable.  
With reference, we can use a value without transferring its ownership.

Here is an example.

```rust
fn main() {
	let s1 = String::from("hello");
	let len = calculate_length(&s1); 
	println!("The length of '{s1}' is {len}."); 
}
fn calculate_length(s: &String) -> usize {
	s.len()
}
```

The following diagram depicts the concept of *reference* in this example.

![[assets/计算机/Programming-Language/Rust/The-Rust-Programming-Language/Chapter 4 Understanding Ownership-1779785528465.jpeg]]

We call the action of creating a reference *borrowing*.  
Like the variable, the reference is immutable by default.

### Mutable References

Using the mutable reference to make the borrowed value modifiable.

```rust
fn main() {
	let mut s = String::from("hello");
	change(&mut s); 
} 
fn change(some_string: &mut String) {
	some_string.push_str(", world");
}
```

The mutable references in Rust is monopoly. That is, a value who has a mutable reference cannot have any other reference.  
Rust uses this rule to prevent *data races* at compile time.  
Moreover, we also cannot create a mutable borrowing when the value is already having a immutable reference.  
Multiple immutable references to a value are allowed.

## The Slice Type

*Slice* allows reference a contiguous sequence of elements in a collection.  
We can create slices using the range within the square brackets `[starting_index..ending_index]`, where the `starting_index` indicate the first position and the `ending_index` is one more than the last position in the slice.  
If the `starting_index` is 0, we can drop it `[..ending_index]`. By the same token, if the slice includes the last item, we can drop the trailing number. Dropping both the starting and ending index will slice the whole collection.
