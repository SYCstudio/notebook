# Chapter 8 Common Collections

## Vectors

We can use vectors to store many items in a single data structure. The items must be the same type.

```rust
// define an empty vector
let v: Vec<i32> = Vec::new();
// define a vector with initial values
let v = vec![1, 2, 3];

// update vector
let mut v = Vec::new();
v.push(2);

// get element from vector
let v = vec![1, 2, 3, 4, 5];
let third: &i32 = &v[2];
println!("The third element is {third}");
let third: Option<&i32> = v.get(2);
match third {
	Some(third) => println!("The third element is {third}"),
	None => println!("There is no third element."),
}

// iterating over vectors
let v = vec![100, 32, 57];
for i in &v {
	println!("{i}");
}
for i in &mut v {
	*i += 50;
}
```

## String

The `String` shares many methods with the `Vector` since `String` is actually implemented as a wrapper around a vector of bytes, with some extra guarantees, restrictions and capabilities.  
The Strings in Rust are UTF-8 encoded.

```rust
// create String
let mut s = String::new();

// create String with initial data
let data = "initial string"
let s = data.to_string(); // any type that implements the Display trait will have a to_string methods
let ss = String::from("initial data");

// use push_str to append a String
let mut s = String::from("foo");
s.push_str("bar"); // note that the 'bar' is a string slice. We don't want to take the ownership of the parameter.
// use push to append a single character
s.push('l');

// use the '+' to combine two exstsing strings
let s1 = String::from("Hello, ");
let s2 = String::from("world!");
let s3 = s1 + &s2; // note s1 has been moved here and can no longer be used

// Combining Strings in more complecated way, uses the format!
let s1 = String::from("tic");
let s2 = String::from("tac");
let s3 = String::from("toe");

let s = format!("{s1}-{s2}-{s3}");
```

Note that, in the above concatenating example, the type of `&s2` is `&String`. However, the add trait's signature looks like `fn add(self, s: &str) -> String {`, who use the type `&str`.  
This can work because the Rust compiler can coerce the `&String` argument into a `&str`. It uses a deref coercion.  
Moreover, the `+` trait moves the ownership of its first parameter (see the signature use `self` instead of `&self`). In the above example, the ownership of `s1` is moved.  
In contrast, the `format!` macro takes all its parameters in the reference format, so their ownership is not moved.

### Indexing into Strings

Rust doesn't allow the common numbering index method on String (like `let c = s[1];`)  
That is because, while the Strings is a wrapper of `Vec<u8>`, the character in UTF-8 is not always one byte.  

At Rust's perspective, there are three relative ways to look at strings.

```rust
// Vector of u8
[224, 164, 168, 224, 164, 174, 224, 164, 184, 224, 165, 141, 224, 164, 164, 224, 165, 135]
// Unicode scalar
['न', 'म', 'स', '्', 'त', 'े']
// Grapheme clusters
["न", "म", "स्", "ते"]
```

Rust allows you to use the `[]` with a range to create a string slice containing particular bytes. However, it still asks the boundary to be valid. The characters must be complete, otherwise the program will panic at runtime.

### Iterating over Strings

The best way to operate on pieces of strings is to be explicit about whether you want characters or bytes.

```rust
// for Unicode scalar view
for c in "Зд".chars() {
    println!("{c}");
}
// result: 
// З
// д

// for byte view
for b in "Зд".bytes() {
    println!("{b}");
}
// result
// 208
// 151
// 208
// 180
```

## Hash Map

The type `HashMap<K, V>` stores a mapping of keys of type K to values of type V, using a *hashing function*.

```rust
// define a hashmap, and insert values into it
use std::collections::HashMap;
let mut scores = HashMap::new();
scores.insert(String::from("Blue"), 10);
scores.insert(String::from("Yellow"), 50);

// get value from a hash map
let team_name = String::from("Blue");
let score = scores.get(&team_name).copied().unwrap_or(0);  // note that the `get` returns an Option<V>

// iterating over a hash map
for (key, value) in &scores {
	println!("{key}: {value}");
}
```

### Managing Ownership in Hash Maps

For types implemented the `Copy` trait, the values are copied into the hash maps.  
Otherwise, the value will be moved.  

In another case, if we insert the reference to the value into the hash map, the value will not be moved.  
However, the value that the reference point to must be valid for at least as long as the hash map is valid.

### Updating in Hash Maps

By default, inserting an existing key into a hash map will overwrite the old one (`.insert`). The hash maps ask the key in the structure must be identical. Each unique key can only have one value associated with it at a time, but not vice versa.  
Hash map also provides some other method of updating, see the following example.

```rust
// adding a key and a value only if the key is not exist
scores.entry(String::from("Yellow")).or_insert(50);
// the entry method is an enum called Entry that represents a value that might or might not exist.
// The or_insert method on Entry is defined to return a mutable reference to the value for the corresponding Entry key if that key exists, and if not, it inserts the parameter as the new value for this key and returns a mutable reference to the new value.

// updating a value based on the old value
use std::collections::HashMap;
let text = "hello world wonderful world";
let mut map = HashMap::new();
for word in text.split_whitespace() {
	let count = map.entry(word).or_insert(0);
	*count += 1;
}
println!("{map:?}");
```

### Hashing Functions

By default, the hash map uses a *SipHash* to store the hashed value.  
We can switch to another function by specifying a different *hasher*, which is a type that implements the `BuildHasher` trait.