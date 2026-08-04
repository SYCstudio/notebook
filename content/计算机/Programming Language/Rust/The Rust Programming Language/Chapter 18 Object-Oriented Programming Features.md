# Chapter 18 Object-Oriented Programming Features

## Characteristics of Object-Oriented Languages

There is no consensus in the programming community about what features a language must have to be considered object oriented.  
However, OOP languages share certain common characteristics: objects, encapsulation, and inheritance.

Object: Object contain data and behavior. Rust provides methods and `impl` for struct and enums.  
Encapsulation: Encapsulation hides implementation details. Rust provides `pub` key to control the visibility of details.  
Inheritance: Rust doesn't allow struct that inherits the parent struct's fields and method implementations. Instead, we can use Rust's trait structure similar but different in many aspects.

## Using Trait Objects to Abstract Over Shared Behavior

We can define a trait for common behavior.  
A trait object points to both an instance of a type implementing our specified trait and a table used to look up trait methods on that type at runtime.   
We create a trait object by specifying some sort of pointer, such as a reference or a `Box<T>` smart pointer, then the `dyn` keyword, and then specifying the relevant trait.  
In trait object, we can't add data to a trait object, as in other languages. Here is an example.

```rust
pub trait Draw {
    fn draw(&self);
}
pub struct Screen {
    pub components: Vec<Box<dyn Draw>>,
}
impl Screen {
    pub fn run(&self) {
        for component in self.components.iter() {
            component.draw();
        }
    }
}
```

This works differently from defining a struct that uses a generic type parameter with trait bounds.   
A generic type parameter can be substituted with only one concrete type at a time, whereas trait objects allow for multiple concrete types to fill in for the trait object at runtime.

### Performing Dynamic Dispatch

Unlink generics, where compiler knows what method we're calling at compile time, Rust must use dynamic dispatch when we use trait object.  
At runtime, Rust uses the pointers inside the trait object to know which method to call. This incurs a runtime cost.

Objectoriented patterns won’t always be the best solution in Rust due to certain features, like ownership, that object-oriented languages don’t have.