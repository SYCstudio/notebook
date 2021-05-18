# pytorch

## tensor 张量
pytorch 中的数组，能自动记录计算过程，自动求导

```python
x = torch.rand(5, 3) # 随机生成一个 5 * 3 的张量
x = torch.ones(5, 3) # 生成全是 1 的张量
x = torch.zeros(5, 3) # 生成全是 0 的张量
x.t() # 转置
y = x.mm(x) # 矩阵乘法
x_tensor = torch.form_numpy(x_numpy) # numpy 转 tensor
x_numpy = x_tensor.numpy() # tensor 转 numpy
x_tensor = torch.FloatTensor(x_numpy) # 指定转换类型
x_numpy = x_tensor.detach().numpy() # 若 tensor 设置了求 grad 后不能之间转成 numpy，要先 detach
```

`tensor` 的很多运算可以放到 GPU 上利用`cuda`加速，首先要判断 GPU 可以正常使用，用`torch.cuda.is_available()`进行验证，如果返回为 True 说明可用。  
使用 `x.cuda()` 来把一个 tensor 放到 GPU 上，使用 `x.cpu()` 取回。

## linespace
用于生成线性数据，返回一个一维 tensor
```python
torch.linspace(start, end, steps, *, out=None, dtype=None, layout=torch.strided, device=None, requires_grad=False) → Tensor
```

## 杂项
### 查看 pytorch 版本
```python
torch.__version__
```
### `torch.rand()`和`torch.randn()`的区别
生成随机数，前者为 $[0, 1)$ 均匀分布，后者为平均值 0 方差 1 的正态分布