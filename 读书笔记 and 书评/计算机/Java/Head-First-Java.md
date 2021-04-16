# Head-First-Java

## Java 中的类
Java 中除基本数据类型以外，其它所有类都是引用，所以都必须 new ，复制的时候也要小心，区分是要复制引用还是值。

## equals() 和 ==
定义上，== 判断的是地址是否相同，而 equals() 判断的是其中的值是否相同。注意，系统定义的类型通常都已经定义有 equals()，而自定义类的 equals() 需要在定义类的时候提前定义好。

> Java 的基类 Object 中对 equals() 的定义也是比较地址，所以如果是从 Object 继承的类需要注意自己定义 equals()
> 基本数据类型(int, double, boolean) 等无 equals() 方法，只能用 == ，但是其对应的封装类型(Integer, Double, Boolean)有 equals() 方法。

## 关于 Object 类
Object 类带有以下方法
```java
boolean equals(Object o);//判断值相同（见上）
Class getClass();//表明该对象是从哪里进行初始化的
int hashCode();//基本的哈希函数，建议自行重载
String toString();//列出类的名字
```
注意 Object 并不是一个抽象的类。

## final 修饰符
final 用来表示到达继承树的末端。如果用 final 修饰类，则说明该类无法继承；如果用 final 修饰方法，则说明该方法无法继承；如果用 final 修饰变量，那么不能改变这个变量的值。
final 用来确保类的安全性。

## 类型转换
用父类引用子类时，仅能调用父类中定义有的方法而不能调用子类的方法。
如果能够确定子类的类型，可以用 (name) 来强制转换。
```java
Object o = new Dog();
Dog d = (Dog) o;
```
如果不能确定，可以用 `instanceof` 运算符来进行检查，如果出现错误会在执行期间抛出 `ClassCastException` 并终止。
```java
if (o instanceof Dog) {
    Dog d = (Dog) o;
}
```

## 接口
在某种程度上实现了多源继承的功能。用 `interface` 代替 `class` 定义接口，在需要“继承” 接口的地方用 `implements` 链接接口。如果有多个接口需要继承，接口之间用 `,` 隔开。
注意到接口实际上已经包含了 abstract 和 public 的意思，所以在接口内部定义方法时可以不用显示地写出。

## 继承与构造函数
在构造函数中若无显式调用父类构造函数，编译器会自动调用不带参数的父类构造函数`super()`。
建议在每一个构造函数开头先调用父类的构造函数。
可以用`this()`调用同一个类中不同的其它构造函数，这样可以省去一部分重复工作。`this()`必须在第一行调用。
注意，`this()`和`super()`不能同时在一个构造函数中调用。

## autoboxing
在 Java5.0 之后引入的特性，将 primitive 数据类型与其对应的对象形式作等价处理，但是注意`ArrayList` 还是只能使用`ArrayList<Integer>`定义因为内部只能是类。