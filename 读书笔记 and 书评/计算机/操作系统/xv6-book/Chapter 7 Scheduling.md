# Chapter 7 Scheduling

任何操作系统都会尝试运行比 CPU 核数更多数量的进程，所以一个如何在让进程分享 CPU 时间的调度方案就显得尤为重要。理想的情况是，操作系统的这些调度对进程完全透明，进程认为自己完全使用 CPU 及其相关硬件资源。

## Multiplexing
xv6 会在两种情况下将 CPU 的使用权从一个进程移交到另一个进程。其一是 xv6 的 sleep 和 wakeup 技术，这一技术使用情况有进程等待设备 I/O， 等待子进程中止，或者是单纯的等待在 sleep 系统调用中。其二是 xv6 会周期性地强制占用 CPU 时间长地进程交出使用权。

## Code: Context switching
下图简要展示了从一个进程切换到另一个进程的过程。首先是一个从旧进程的用户到旧进程的内核的过程（可能是系统调用或者中断），然后是切换到当前 CPU 的调度进程，再是切换到新的进程的内核，最后是通过 trap ret 返回到新进程的用户态。xv6 对于每一个 CPU 安排了一个独有的调度进程，因为如果直接使用旧进程的 kernel stack 并不安全（可能其它 CPU 在此时唤醒该进程，导致两个核同时使用同一个 kernel stack，出现混乱）。

![](_v_images/20220316212617891_15776.png)

从一个进程切换到另一个进程首先要考虑的就是保存旧进程的 CPU 寄存器，并恢复即将运行的进程的相关寄存器，这些信息统称为 `context`。函数 `swtch` 就是用于将两个 context 交换，当应用到当前场景时，kernel 首先将当前进程的 context 与所在 CPU 的调度进程的 context 交换。一个值得注意的点是，swtch 仅保存 callee-saved 寄存器，caller-saved 寄存器的信息是由调用函数保存在栈中的。同时它并不保存 PC 而是保存 ra 表示 swtch 被调用时的地址用于返回。这意味着 swtch 返回的并不是之前调用它的函数，而是交换之后的新的 ra。

## Code: Scheduling
现在我们来关注 `scheduler` 函数，这个函数在每个 CPU 上独有一份，用于决定接下来在这个 CPU 上运行哪一个进程。一个想要放弃 CPU 的进程必须持有自己的 lock 并且释放其它所有的 lock，更新它自己的 state 为 `RUNNABLE`，再调用 sched 开始接收调度程序的调度。sched 会进行 lock 和 state 等内容的检查，如果错误会抛出 panic，否则进行 context switch 进入 CPU 的进程调度程序 scheduler。  
注意到这一过程中对于锁 lock 的使用是不寻常的。通常来说，持有锁的进程负责释放锁，但是在这里是由 yield 或其它什么程序持有锁，然后通过 context switch 交换到 scheduler 程序继续持有锁，再由 scheduler 释放锁。反过来从 scheduler 返回到进程的时候，则是先由 scheduler 程序加锁，通过 context switch 交换到比如 yield 然后释放锁。造成这一异常的是，由该锁保护的程序变量在 context switch 过程中是不安全的，所以必须要使用锁来保护，但是 switch 前后切换了执行的程序，所以需要两个程序配合完成锁的操作。

## Code: mycpu and myproc
xv6 为每一个 CPU 维护了一个 struct cpu 结构，用于保存当前 CPU 的全部数据。RISC-V 给每一个 CPU 一个编号 hartid。xv6 保证每个 CPU 在运行在 kernel 时 CPU 的 hartid 保存在寄存器 tp 中，并且允许 mycpu 通过这一寄存器识别当前 CPU 。要保证 tp 的这一性质需要在多个地方加入设定，比如在 mstart 启动期间（机器模式下）为每一个 CPU 设置 tp，在 usertrapret 的时候将 tp 保存到 trapframe （因为用户进程可能会使用到 tp），在 uservec 的时候从 trapframe 恢复 tp，编译器保证 xv6 系统程序不会使用到 tp 这一寄存器。  
mycpu 和 cpuid 的返回值是脆弱的，因为若在这之后发生了中断然后导致了进程切换，返回值会由于进程调度而失效。所以要求调用这两个函数的时候都要屏蔽中断。一个例子是 myproc() 函数，这一函数在调用 mycpu 前先屏蔽了中断，等拿到需要的 proc 的指针后再恢复中断。myproc 的返回值是安全的，因为即使发生了中断，proc指针的值仍然是有效的。

## Sleep and wakeup
xv6 使用了 sleep 和 wakeup 的技术允许一个进程因等待某个事件而睡眠，另一个进程应答事件唤醒该进程。  
这一过程中涉及到多个锁的操作，尤其是 sleep，由于要求锁必须在 sleep 开始执行后才能释放（否则会引发 race），sleep 的参数是两个：`sleep(chan, lock)` 其中前一个是 sleep 和 wakeup 用于通信的 channel 编号（具体是什么随意），后一个则是触发这个 sleep 的锁。  
一个使用了 sleep 和 wakeup 的复杂例子是 pipe，它维护了一个循环队列用于缓存，然后使用锁来解决生产者和消费者之间的各种问题。

## Real world
xv6 实现了比较简单的进程调度方式，现代操作系统的进程调度通常会更加复杂，比如将不同进程赋予不同优先级，同时要保证公平性和足够的吞吐量。  
在 sleep 和 wakeup 的方面，各个操作系统也有不同的选择。早期 Unix 由于是运行在单一核上，所以粗暴地简单屏蔽所有中断；xv6 采用对 sleep 加锁的办法，FreeBSD 与之类似；Linux 使用了进程等待队列，队列自身需要一个锁。  
同样，xv6 中在 wakeup 中扫描所有的进程槽其实也是低效的。现代操作系统会将 channel 换成更为复杂的数据结构，这个数据结构类似地保存了所有在等待队列中的进程，在唤醒的时候更加有效率。这里实现的 wakeup 的另一个低效之处是它会唤醒所有等待的进程，现代操作系统则通常提供 signal 和 broadcast 的区别，前者仅唤醒一个进程，而后者唤醒所有进程。
