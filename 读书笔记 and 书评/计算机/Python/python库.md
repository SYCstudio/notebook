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

## argparse 库
用于处理输入参数的库，能格式化地解析在命令行输入的参数，并提供配置好的帮助文档。  
具体使用的时候，首先定义一个 `ArgumentParser()`，然后使用 `add_argument()` 函数添加需要解析的参数。在这一函数中，可以指定参数缩写、全程、是否带参数、是否必选、默认值等。另外使用函数`add_mutually_exclusive_group()`可以指定互斥参数。  
最后，当所有的配置完成后，调用函数`parse_args()`可以进行解析。函数首先会对参数的合法性、必选参数是否已填、互斥参数是否满足等进行检查，如果通过，解析后直接访问返回的类中的对应名字就可以访问参数，非常方便。  
下面给出一个例子

```python
parser = argparse.ArgumentParser()
agent_selector = parser.add_mutually_exclusive_group(required=True)
agent_selector.add_argument("-q", "--qlearning", action="store_true", help="running qlearning algorithm")
agent_selector.add_argument("-p", "--policygradient", action="store_true", help="running policy gradient algorithm")

train_or_test = parser.add_mutually_exclusive_group(required=True)
train_or_test.add_argument("-tn", "--train", action="store_true", help="running on training mode")
train_or_test.add_argument("-tt", "--test", action="store_true", help="running on testing mode(must load an exist model file, use -l option)")

parser.add_argument("-g", "--gui", action="store_true", help="show gui(default: false)")
parser.add_argument("-s", "--save_model", help="save model(default: false)", dest="interval", type=int)
parser.add_argument("-l", "--load_model", help="load model from file", dest="filename")
```

## Rich 库
提供颜色化的终端输出

其中 rich.progress 中的 track 可以提供进度条

[主页](https://rich.readthedocs.io/en/stable/introduction.html)

## tqdm 库
提供简单的进度条功能

[参考](https://zhuanlan.zhihu.com/p/163613814)
