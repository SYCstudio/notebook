# Chapter 6 Locking

不论是在多核系统，还是单核系统，由于内核将进程划分到时间片执行，都有可能出现竞争情况（即同时写，或同时读写），破坏数据的一致性。内核自身就使用了很多需要一致访问的数据结构，并且使用了一些一致性控制的技术来保护这些部分。下面主要关注一个广泛使用的技术：锁 lock。  
锁提供了一种独占访问机制，保证在任意时刻只能有一个 CPU 持有该锁，若将该锁与需要保护的数据结构绑定，则可以保证该数据结构在任意时刻只被最多一个 CPU 访问。  
锁能有效地提供互斥访问，但是这是以牺牲效率作为代价的，因为锁强制进程以线性而非并行方式运行。

## Race conditions
当某一内存地址被多个进程同时访问，且至少有一个进程需要写入时，就出现了竞争条件 race conditions 的情况。竞争条件会带来严重的后果，可能是多个写入的冲突，也有可能是读取了旧的数据。由于其特殊性，这种错误比较难复现和调试。  
解决竞争条件的最常用的办法就是使用锁，在访问竞争数据前要求 CPU 必须持有绑定的锁，这样保证只有一个进程能与数据交互。  
由于锁的使用会带来性能的损失，所以通常需要仔细设计使得要保护的内容尽可能少，以最大化并行效率。

## Code: Locks
xv6 中提供了两种锁： spinlock 和 sleep-lock。先讨论前者。spinlock 使用了 RISC-V 提供的原子指令来操作锁，`amoswap r, a` 将内存地址中 r 的值与寄存器 a 中的值交换，使得读写操作在一个周期内完成并且在硬件层面阻止其它进程的访问。xv6 使用 C 语言中提供的宏 ` __sync_lock_test_and_set` ，这是一个对 `amoswap` 的封装，传入新值返回旧值。如果返回值是 0 ，说明当前 CPU 获得了该锁，并将其置为 1；如果返回值是 1 则说明该锁被其它进程占用。spinlock 的关键部分代码如下

```c
void
acquire(struct spinlock *lk)
{
  push_off(); // disable interrupts to avoid deadlock.
  if(holding(lk))
    panic("acquire");

  // On RISC-V, sync_lock_test_and_set turns into an atomic swap:
  //   a5 = 1
  //   s1 = &lk->locked
  //   amoswap.w.aq a5, a5, (s1)
  while(__sync_lock_test_and_set(&lk->locked, 1) != 0)
    ;

  // Tell the C compiler and the processor to not move loads or stores
  // past this point, to ensure that the critical section's memory
  // references happen strictly after the lock is acquired.
  // On RISC-V, this emits a fence instruction.
  __sync_synchronize();

  // Record info about lock acquisition for holding() and debugging.
  lk->cpu = mycpu();
}
```

释放锁的 `release` 函数与 `acquire` 函数类似。

## Code: Using locks
一个关于锁的难点在于如何确定使用锁的数量以及哪些数据需要用锁来保护。有以下几条简单的原则可供考虑：其一是，对于那些可能被一个 CPU 写同时被另一个 CPU 读或写的数据，需要使用锁来保证两个操作互斥。其二是不变量 invariant（这里指在完成操作前后保持一定结构的数据，由于中间操作可能临时破坏结构，所以会出现竞争条件），需要使用锁来保证每一次对不变量修改都是原子化的。  
上述规则描述了使用锁的必须情况，但并未描述不需要使用锁的情况。考虑到使用过多的锁会显著降低并行度，如何合理地设计锁使用的范围也很重要。在将一些早期单进程内核移植到多核机器上时，常常使用 big kernel lock 的技巧将这个内核用锁保护起来，这样虽然便于移植，但显著地牺牲了可并行性。关于 xv6 中使用过的仔细设计锁的技巧，可以参考 `kalloc.c` 和对 file 的锁。更加仔细的文件锁的设计或许可以允许多个进程同时写文件的不同部分，但是这意味着编码复杂度的提升。我们需要在运行效率和代码复杂度中作一些权衡和取舍。

## Deadlock and lock ordering
当一些程序需要获得多个锁的时候，如何设计锁的获得顺序以防止出现死锁也是一个值得考虑的问题。  
为了避免死锁，通常要求程序均以相同的顺序获得锁。这一顺序需要提前设计好，并且为所有的进程遵守，但是由于并不知道具体程序设计，确定一个合理的顺序通常是很难的。

## Locks and interrupt handlers
当锁与中断同时出现时，情况会变得更加负责。考虑一个 `clockintr` 时间中断处理程序，需要对一个数据 `ticks` 进行操作，同时内核进程 `sys_sleep` 要读取这个数据。如果采用常规的锁，内核读取的时候会对 `ticks`加锁，同时这时出现一个时间中断，跳转到 `clockintr` 也要获得这个锁，但是这个锁被 `sys_sleep` 占据，但中断返回之前内核不会释放该锁，这样就造成了一个死锁情况。    
为了避免这样的情况发生，规定如果一个锁可能被中断程序使用，CPU 必须在中断被屏蔽的情况下才能获得这个锁。xv6 采用了一种更保守的做法，当 CPU 获得任何锁的时候，xv6 都会屏蔽这个 CPU 上的任何中断。在这种情况下，中断依然有可能发生在其它 CPU 上，此时让中断等待当前进程释放锁即可。由于保证了中断和获得锁的进程出现在不同的 CPU 上，这一方法是有效的。

## Instruction and memory ordering
通常我们会自然地认为，程序真实执行的顺序是与源代码中的顺序一致的，但遗憾的是，现代 CPU 为了充分利用计算资源加快运行速度，会自动地进行乱序执行。通常来说， CPU 的乱序执行规则会保证执行结果与顺序执行的一致，但当涉及到与锁相关的代码时，相关识别可能会出现问题。  
为了保证顺序，防止编译器和硬件擅自重排，xv6 在合适的地方使用函数 `__sync_synchronize()`作为内存屏障，告知编译器和运行硬件不允许将该屏障前后的代码调换执行顺序（即强制该屏障之后的代码都必须在屏障前代码之后执行）

## Sleep locks
有些时候，一些程序可能需要长时间持有一个锁。如果均采用 spinlock 中那样的循环模式，对于其它等待锁的进程可能会造成大量的运算浪费。  
xv6 中提供了另一种锁 sleep lock 来尝试解决这一问题。一个对 sleep lock 的简单概括是，sleep lock 是一个被 spinlock 保护的数据区域，并且它能够在等待的时候原子化地主动 yield 释放计算资源和 spinlock 。这样其它的进程就可以来执行。  
由于 sleep lock 没有屏蔽中断，所以不能用在与中断有关的锁上；又由于它会主动让出 CPU ，所以不能在 spinlock 中使用（但反过来是可以的）。

## Real world
使用非原子化指令来实现锁是有可能的，但代价太高，所以大部分的操作系统都是使用依赖硬件的原子操作来实现锁。  
现代存储体系中的 cache 让锁的使用变得复杂。cache 的设计和使用者必须仔细考虑竞争锁时 cache 失效的相关问题，比如一个 CPU 获得锁的同时要让其它 CPU 的 cache 中的相关行失效。  
由于使用锁的代价还是太大，很多现代操作系统会使用 lock-free 的数据结构和算法，但这与使用锁相比大大增加了编程的难度。
