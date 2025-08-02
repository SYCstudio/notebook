# Programming in Lua

[4th edition]

## The Basics

使用 `--[[` 和 `]]` 来标记注释。比较方便的做法如下。

注释：

```lua
--[[
     a = 10
--]]
```

取消注释：

```lua
---[[
    a = 10
--]]
```

Lua 不是强类型的语言，任何一个全局变量名初始时默认是 nil （这是一种只有这一种取值的类型）。

Lua  的类型中包含 Boolean，其取值为 true 或 false（大小写均可）。  
Lua 的逻辑判断将所有的 false 和 nil 认为是假，其他的所有认为是真（即认为数字 0 和空字符串为真）。  
一个可能有用的语法糖（可能用于赋初值？）：

```lua
x = x or v

--[[
    which equals to:
    if not x then v = v end
]]
```

Lua 中的 and 和 or 均有运算结果。  
对于 and 运算，如果它的第一个操作数为假，则运算结果为第一个操作数，否则为第二个操作数。  
对于 or 运算，如果它的第一个操作数不为假，则运算结果为第一个操作数，否则为第二个操作数。  
基于上述特性，有 Lua 的三目运算符写法如下：

```lua
x = a and b or c
x = (a and b) or c --Lua 中 and 优先级更高

--[[
    which equals to :
    x = a ? b : c; in C
]]
```

Lua 在语言层面不区分实数和整数，统一用 number 类型来表示。  
Lua5.3 在具体实现层面引入了对实数和整数的区分，在一般的机器上分别实现为 `int64` 和 `float64`。  
只有参与运算的所有变量均为整数时，结果才会是整数。  

Lua 中的字符串均为 uint8 常量值，不支持定义后修改。字符串的 index 从 1 开始。   
Lua 使用如下方式表示跨行长字符串，其中 `\z` 忽略之后的空白字符。

```lua
s1 = [[
this
is
a
long
string
]]

s2 = "aaaaa\z
      bbbbb"
```

在面对数字和字符串混合的运算时，Lua 会尝试进行类型转换。但如果在比较运算中出现了混合，Lua 会抛出异常。

```lua
print(10 .. 20) --> 1020
10 < "20" --> raise an error
```

Lua  的 table 类型是一个关联数组（类似 python 中的 dict），允许使用数字和字符串作为索引。字符串索引可以以点的方式访问。

```lua
a = {}
a.x = 10 --> same as a["x"] = 10

days = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"} --> days[1] = "Sunday"

a = {x = 0, y = 0} --> {["x"] = 0, ["y"] = 0}
a = {"r", "g", "b"} --> {[1] = "r", [2] = "g", [3] = "b"}
```

Lua 中的数组（其实就是上面的 table）并不要求一定从 1 开始标号，但一些内部特性依赖这一点，所以一般都以 1 作为数组的起始标号。

Lua 中的函数定义，允许传入更少或更多的参数，未赋值的参数被置为 nil（可以用于设置默认值），多余的参数会被丢弃。  
Lua 函数允许多个返回值，使用逗号隔开即可。函数返回值的数量与实际赋值给的数量也可以不同，其参考处理办法与传入参数相同。  
函数返回值仅有在处于一个 list 末尾时才进行上述补全或丢弃，如果出现在一个 list 的非末尾，只会取第一个值。下面是一些例子：

```lua
function foo0 () end -- returns no results
function foo1 () return "a" end -- returns 1 result
function foo2 () return "a", "b" end -- returns 2 results

x, y = foo2() -- x="a", y="b"
x = foo2() -- x="a", "b" is discarded
x, y, z = 10, foo2() -- x=10, y="a", z="b"

x,y = foo0() -- x=nil, y=nil
x,y = foo1() -- x="a", y=nil
x,y,z = foo2() -- x="a", y="b", z=nil

x,y = foo2(), 20 -- x="a", y=20 ('b' discarded)
x,y = foo0(), 20, 30 -- x=nil, y=20 (30 is discarded)
print(foo0()) --> (no results)
print(foo1()) --> a
print(foo2()) --> a b
print(foo2(), 1) --> a 1
print(foo2() .. "x") --> ax (see next)

t = {foo0(), foo2(), 4} -- t[1] = nil, t[2] = "a", t[3] = 4

print((foo0())) --> nil
print((foo1())) --> a
print((foo2())) --> a
```

Lua 中使用 `...` 来表示变长的函数参数。在函数内部也是使用这一标识符来取得该函数参数。  
`...` 的行为和一个返回多个结果的函数类似。  
变长的函数参数允许在其前面定义若干固定的函数参数。  
通常可以使用 `{...}` 来把变长的函数参数打包成一个 table，但当变长函数参数中含有 nil 的时候这个方法会出问题。推荐使用 `table.pack(...)` 来打包，这个打包后会包含一个键值 n 表示长度。对应的有 `table.unpack()`。  

Lua 中的包 `strict.lua` 允许对程序中使用到的全局变量严格检查，当我们尝试在函数中对不存在一个全局变量赋值或者使用一个不存在的全局变量时，会抛出错误。

## Real Programming

Lua 中创建闭包的语法糖：`foo = function(x) return 2 * x end`。  
在前面加上 `local` 关键字则将改闭包变为本地函数（local function）。  
本地函数不能直接自递归调用，需要提前定义好。下面是一个例子。

```lua
local fact = function(n)
    if n == 0 then return 1
    else return n * fact(n-1) --buggy
    end
end

local fact
fact = function(n)
    if n == 0 then return 1
    else return n * fact(n-1) --ok
    end
end
```

Lua 的闭包函数能访问外部的变量。但采用闭包的形式使得相互之间不会干扰。下面是一个例子：

```lua
function newCounter ()
    local count = 0
    return function () -- anonymous function
        count = count + 1
        return count
    end
end
c1 = newCounter()
print(c1()) --> 1
print(c1()) --> 2
c2 = newCounter()
print(c2()) --> 1
print(c1()) --> 3
print(c2()) --> 2
```

准确来说，Lua 中存放在值中的是闭包而不是函数，函数应该被理解为用于定义闭包的原型。

