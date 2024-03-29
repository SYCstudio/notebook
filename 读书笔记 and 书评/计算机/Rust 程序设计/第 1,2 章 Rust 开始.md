# 第 1,2 章 Rust 开始

`Rust` 安装后，提供了以下几个工具

* `cargo` 是编译管理器，包管理器以及通用工具。使用 `cargo` 来创建新项目，构建和运行程序，以及管理外部库
* `rustc` 是编译器，通常由 `cargo` 来调用它
* `rustdoc` 是文档工具。`rustdoc` 能根据合适的代码注释生成 HTML 说明文档，通常由 `cargo` 来调用它。

命令 `cargo new --bin name` 用于创建新项目，其中 `--bin` 指明生成的是可执行文件而不是库文件。命令 `cargo run` 构建并运行程序。命令 `cargo clean` 清理生成的文件。  
`Rust` 中整数类型指出了它的大小以及有无符号，比如 `i32, u32, isize` 分别表示有符号 32 位整数、无符号 32 位整数、指针大小有符号整数，另有浮点类型 `f32,f64`。  
默认情况下，一个变量初始化后就不能再改变。在变量前加 `mut` (mutable)关键字能使之被修改。  
`assert!` 宏用于验证其参数是否不为 0 ，其中 `!` 标明这是一个宏而非函数调用。`debug_assert!` 宏与之类似，但当程序为速度编译时会略过。  
`let` 用于声明一个局部变量，通常是可以由 `Rust` 自身推断类型，也可以指定类型 `let m : u32 = 10`。  
`Rust` 有 `return` 语句，但同时如果一个函数体的最后一行代码是一个表达式且不以分号结尾，那么这个表达式就是函数体的返回值。  
在函数前设置 `#[test]` **属性**来使用 `Rust` 本身内置的简单测试机制，这一函数在常规编译中会被跳过，但通过 `cargo test` 编译运行时会包含并自动调用。属性是一种开放式标记，用于给函数或其他声明添加补充说明。  
原始字符串，在 `r` 后接任意多个 `#` 然后再是一个双引号，再接字符串内容，最后再在最后的双引号后加上等量的 `#`。原始字符串中的任意字符都不需要转义。总能够添加足够多的 `#` 来避免歧义。  
类型 `Option` 是枚举，`Rust` 语言中是这样定义的：

```rust
enum Option<T> {
    None,
    Some(T),
}
```

`//` 表示注释，`///` 表示文档注释。文档注释可以用来生成说明文档。