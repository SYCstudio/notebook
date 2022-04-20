# python库

关于 python 中的赋值、引用、拷贝：[link](https://draapho.github.io/2016/11/21/1618-python-variable/)

## sqlite3 库
一个控制 sqlite 的库。

引入方式：`import sqlite3`

[link](https://www.runoob.com/sqlite/sqlite-python.html)

## unittest库
用于单元测试的库，创建继承自 `unittest.TestCase` 的测试类，然后在类中添加测试函数。调用`.main()`来自动运行所有测试。

该模块同时提供了以下方法用于断言

|        方法        | 用途 |
| ------------------ | ---- |
| `assertEqual(a,b)` |核实`a==b`      |
|`assertNotEqual(a,b)`|核实 `a!=b`|
|`assertTrue(x)`|核实`x==True`|
|`assertFalse(x)`|核实`x==False`|
|`assertIn(item,list)`|核实`item`在`list`中|
|`assertNotIn(item,list)`|核实`item`不在`list`中|

可以在每一个测试函数中都重新创建相应的实例并初始化，但同时该模块中还提供了`setUp()`方法来统一创建并初始化实例，使得只需要初始化一次就可以在所有测试中使用。如果在类中包含了`setUp()`函数，Python将会先运行它，然后再运行所有以`test_`开头的方法。  
类似的，该模块提供了`tearDown()`来进行扫尾工作。值得注意的是，无论测试方法是否成功，都会运行`tearDown()`
