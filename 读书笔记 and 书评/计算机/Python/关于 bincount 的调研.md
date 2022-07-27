# 关于 bincount 的调研

函数基本功能：统计输出的 1D 数组中的每一个元素出现的次数，如果有 `weight` 参数则还需要加入

## Pytorch: torch.bincount
函数原型：`torch.bincount(input, weights=None, minlength=0) → Tensor`

源码部分：  
CPU 版本：使用 for 一个一个加

```cpp
namespace at { namespace native {

///////////////// bincount /////////////////
namespace {
template <typename input_t, typename weights_t>
Tensor _bincount_cpu_template(
    const Tensor& self,
    const Tensor& weights,
    int64_t minlength) {
  if (minlength < 0) {
    AT_ERROR("minlength should be >= 0");
  }
  if (self.dim() == 1 && self.numel() == 0) {
    return native::zeros({minlength}, kLong);
  }
  if (self.dim() != 1 || *self.min().data_ptr<input_t>() < 0) {
    AT_ERROR("bincount only supports 1-d non-negative integral inputs.");
  }

  bool has_weights = weights.defined();
  if (has_weights && weights.size(0) != self.size(0)) {
    AT_ERROR("input and weights should have the same length");
  }

  Tensor output;
  int64_t self_size = self.size(0);
  int64_t nbins = static_cast<int64_t>(*self.max().data_ptr<input_t>()) + 1L;
  nbins = std::max(nbins, minlength); // at least minlength # of bins

  const input_t* self_p = self.data_ptr<input_t>();
  if (has_weights) {
    output = native::zeros(
        {nbins},
        optTypeMetaToScalarType(weights.options().dtype_opt()),
        weights.options().layout_opt(),
        weights.options().device_opt(),
        weights.options().pinned_memory_opt());
    weights_t* output_p = output.data_ptr<weights_t>();
    const weights_t* weights_p = weights.data_ptr<weights_t>();
    for (const auto i : c10::irange(self_size)) {  //-------------------------------在这里加，此处是带有 weight 参数的--------------------
      output_p[self_p[i]] += weights_p[i];
    }
  } else {
    output = native::zeros({nbins}, kLong);
    int64_t* output_p = output.data_ptr<int64_t>();
    for (const auto i : c10::irange(self_size)) { //-------------------------------在这里加，此处是无 weight 参数的--------------------
      output_p[self_p[i]] += 1L;
    }
  }
  return output;
}
} // namespace

Tensor
_bincount_cpu(const Tensor& self, const c10::optional<Tensor>& weights_opt, int64_t minlength) {
  // See [Note: hacky wrapper removal for optional tensor]
  c10::MaybeOwned<Tensor> weights_maybe_owned = at::borrow_from_optional_tensor(weights_opt);
  const Tensor& weights = *weights_maybe_owned;

  return AT_DISPATCH_INTEGRAL_TYPES(self.scalar_type(), "bincount_cpu", [&] {
    const auto scalar = weights.scalar_type();
    if (scalar == ScalarType::Undefined || scalar == ScalarType::Float)
      return _bincount_cpu_template<scalar_t, float>(self.contiguous(), weights.contiguous(), minlength);
    return _bincount_cpu_template<scalar_t, double>(
        self.contiguous(), weights.contiguous().to(kDouble), minlength);
  });
}
```

cuda 版本：调用 `CUDA_tensor_histogram`

```cpp
namespace {
///////////////// bincount /////////////////
template <typename input_t, typename weights_t>
Tensor _bincount_cuda_template(
    const Tensor& self,
    const Tensor& weights,
    int64_t minlength) {
  if (minlength < 0) {
    AT_ERROR("minlength should be >= 0");
  }
  if (self.dim() == 1 && self.numel() == 0) {
    return native::zeros(
        {minlength},
        kLong,
        c10::nullopt /* layout */,
        kCUDA,
        c10::nullopt /* pin_memory */);
  }
  if (self.dim() != 1 ||
      (!std::is_same<input_t, uint8_t>::value &&
       *self.min().cpu().data_ptr<input_t>() < 0)) {
    AT_ERROR("bincount only supports 1-d non-negative integral inputs.");
  }

  bool has_weights = weights.defined();
  if (has_weights && weights.size(0) != self.size(0)) {
    AT_ERROR("input and weights should have the same length");
  }

  const int64_t nbins =
      std::max(self.max().item<input_t>() + (int64_t)1, minlength);

  // we are using acc_type for the bounds, in particular int64_t for integers
  // in order to avoid overflows (e.g. using 256 bins for dtype uint8)
  using bounds_t = at::acc_type<input_t, /*is_cuda=*/true>;
  const bounds_t minvalue = 0;
  const bounds_t maxvalue = nbins;
  // alloc output counter on GPU
  Tensor output;
  if (has_weights) {
    output = native::zeros(
        {nbins},
        optTypeMetaToScalarType(weights.options().dtype_opt()),
        weights.options().layout_opt(),
        weights.options().device_opt(),
        weights.options().pinned_memory_opt());
    cuda::CUDA_tensor_histogram<weights_t, input_t, true>(
        output, self, weights, nbins, minvalue, maxvalue);
  } else {
    output = native::zeros(
        {nbins},
        kLong,
        c10::nullopt /* layout */,
        DeviceType::CUDA,
        c10::nullopt /* pin_memory */);
    cuda::CUDA_tensor_histogram<int64_t, input_t, false>(
        output, self, weights, nbins, minvalue, maxvalue);
  }
  return output;
}

///////////////// histc /////////////////
template <typename input_t>
Tensor _histc_cuda_template(
    const Tensor& self,
    int64_t nbins,
    at::acc_type<input_t, /*is_cuda=*/true> min,
    at::acc_type<input_t, /*is_cuda=*/true> max) {
  if (nbins <= 0) {
    AT_ERROR("bins must be > 0");
  }
  Tensor output = native::zeros(
      {nbins},
      self.scalar_type(),
      c10::nullopt /* layout */,
      DeviceType::CUDA,
      c10::nullopt /* pin_memory */);
  input_t minvalue = min;
  input_t maxvalue = max;
  if (min == max && self.numel() > 0) {
    minvalue = *self.min().cpu().data_ptr<input_t>();
    maxvalue = *self.max().cpu().data_ptr<input_t>();
  }
  if (minvalue == maxvalue) {
    minvalue = minvalue - 1;
    maxvalue = maxvalue + 1;
  }

#if !defined(USE_ROCM)
  TORCH_CHECK(
      !(at::_isinf(minvalue) || at::_isinf(maxvalue) ||
        at::_isnan(minvalue) || at::_isnan(maxvalue)),
      "range of [",
      minvalue,
      ", ",
      maxvalue,
      "] is not finite");
#else
  TORCH_CHECK(
      !(std::isinf(minvalue) || std::isinf(maxvalue) || std::isnan(minvalue) ||
        std::isnan(maxvalue)),
      "range of [",
      minvalue,
      ", ",
      maxvalue,
      "] is not finite");
#endif
  TORCH_CHECK(minvalue < maxvalue, "max must be larger than min");

  cuda::CUDA_tensor_histogram<input_t, input_t, false>(
      output, self, Tensor(), nbins, minvalue, maxvalue);
  return output;
}
} // namespace
```

其中 `CUDA_tensor_histogram` 的实现如下：

```cpp
/*
  Calculate the frequency of the input values.

  `a` contains the final output or the histogram.
  Input `b` is assumed to be 1-D non-negative int array.
  `c` optionally contains the weight vector.
  See `help torch.bincount` for details on the math.

  3 implementations based of input size and memory usage:
    case: #bins < THRESH_NUMBER_BINS_FOR_MULTI_BLOCK_MEM and enough shared mem
        SHARED: Each block atomically adds to it's own **shared** hist copy,
        then atomically updates the global tensor.
    case: #bins < THRESH_NUMBER_BINS_FOR_GLOBAL_MEM and enough global mem
        MULTI_BLOCK: Each block atomically adds to it's own **global** hist
        copy, then atomically updates the global tensor.
    case: THRESH_NUMBER_BINS_FOR_GLOBAL_MEM <= #bins
        GLOBAL: all threads atomically update to a single **global** hist copy.
 */
template <typename output_t, typename input_t, bool HasWeights>
bool CUDA_tensor_histogram(
    at::Tensor a, /* output */
    at::Tensor b, /* input */
    at::Tensor c, /* weights(optional) */
    int64_t nbins,
    at::acc_type<input_t, /*is_cuda=*/true> minvalue,
    at::acc_type<input_t, /*is_cuda=*/true> maxvalue,
    TensorArgType aType = TensorArgType::ReadWrite,
    TensorArgType bType = TensorArgType::ReadOnly,
    TensorArgType cType = TensorArgType::ReadOnly) {
  checkBackend("CUDA_tensor_histogram", {a, b}, Backend::CUDA);
  if (HasWeights) {
    checkBackend("CUDA_tensor_histogram", {c}, Backend::CUDA);
  }
  auto totalElements = b.numel();

  if (totalElements == 0) {
    return false;
  }

  const dim3 block = getApplyBlock();
  dim3 grid;
  int64_t curDevice = current_device();
  if (curDevice == -1 || !getApplyGrid(totalElements, grid, curDevice)) {
    return false;
  }

  CUDAHistogramMemoryType memType = CUDAHistogramMemoryType::GLOBAL;
  auto maxSharedMem = getCurrentDeviceProperties()->sharedMemPerBlock;
  auto sharedMem = nbins * sizeof(output_t) + 8; // 8 guard bytes
  auto maxGlobalMem = getFreeGlobalMemory();
  auto multiBlockMem = nbins * grid.x * sizeof(output_t) + 8; // 8 guard bytes
  // determine memory type to use in the kernel
  if (nbins < THRESH_NUMBER_BINS_FOR_MULTI_BLOCK_MEM &&
      sharedMem < maxSharedMem) {
    memType = CUDAHistogramMemoryType::SHARED;
  } else if (
      nbins < THRESH_NUMBER_BINS_FOR_GLOBAL_MEM &&
      multiBlockMem < (maxGlobalMem / 2)) {
    // check against half of free mem to be extra safe
    // due to cached allocator, we may anyway have slightly more free mem
    memType = CUDAHistogramMemoryType::MULTI_BLOCK;
  }

  // alloc memory for MULTI_BLOCK
  using IndexType = int64_t;
  auto aInfo = detail::getTensorInfo<output_t, IndexType>(a);
  auto bInfo = detail::getTensorInfo<input_t, IndexType>(b);
  detail::TensorInfo<output_t, IndexType> pInfo(nullptr, 0, {}, {});
  Tensor partial_output;
  if (memType == CUDAHistogramMemoryType::MULTI_BLOCK) {
    partial_output = native::zeros(
        {grid.x, nbins},
        optTypeMetaToScalarType(a.options().dtype_opt()),
        a.options().layout_opt(),
        a.options().device_opt(),
        a.options().pinned_memory_opt());
    pInfo = detail::getTensorInfo<output_t, IndexType>(partial_output);
  }

  if (HasWeights) {
    auto cInfo = detail::getTensorInfo<output_t, IndexType>(c);
    const auto getWeightsOp = [cInfo] __device__(IndexType cIndex) {
      const IndexType cOffset =
          detail::IndexToOffset<output_t, IndexType, 1>::get(cIndex, cInfo);
      return cInfo.data[cOffset];
    };
    HANDLE_SWITCH_CASE(memType, getWeightsOp)
  } else {
    static const auto getDummyOp = [] __device__(IndexType) { return 1L; };
    HANDLE_SWITCH_CASE(memType, getDummyOp)
  }
  return true;
}
```

其中最后 `HANDLE_SWITCH_CASE` 中宏定义是对几种情况的区别调用，最后都会进入到一下 `cuda KERNEL` 函数

```cpp
template <
    typename output_t,
    typename input_t,
    typename IndexType,
    int ADims,
    int PDims,
    int BDims,
    CUDAHistogramMemoryType MemoryType = CUDAHistogramMemoryType::MULTI_BLOCK,
    typename Op>
C10_LAUNCH_BOUNDS_1(cuda::getApplyBlockSize())
__global__ void kernelHistogram1D(
    detail::TensorInfo<output_t, IndexType> a, /* output */
    detail::TensorInfo<output_t, IndexType> p, /* partial output */
    detail::TensorInfo<input_t, IndexType> b, /* input */
    int64_t nbins,
    at::acc_type<input_t, /*is_cuda=*/true> minvalue,
    at::acc_type<input_t, /*is_cuda=*/true> maxvalue,
    IndexType totalElements,
    Op getOp) {
  extern __shared__ unsigned char my_smem[];
  output_t* smem = nullptr;

  if (MemoryType == CUDAHistogramMemoryType::SHARED) {
    ////////////////////////// Shared memory //////////////////////////
    // atomically add to block specific shared memory
    // then atomically add to the global output tensor
    smem = reinterpret_cast<output_t*>(my_smem);
    for (IndexType i = threadIdx.x; i < a.sizes[0]; i += blockDim.x) {
      smem[i] = 0;
    }
    __syncthreads();
    FOR_KERNEL_LOOP(linearIndex, totalElements) {
      // Convert `linearIndex` into an offset of `b`
      const IndexType bOffset =
          detail::IndexToOffset<input_t, IndexType, BDims>::get(linearIndex, b);
      const auto bVal = b.data[bOffset];
      if (bVal >= minvalue && bVal <= maxvalue) {
        // Use value at `b` as an offset of `smem`
        const IndexType bin =
            getBin<input_t, IndexType>(bVal, minvalue, maxvalue, nbins);
        gpuAtomicAddNoReturn(&smem[bin], getOp(linearIndex));
      }
    }
    __syncthreads();
    // NOTE: atomically update output bin count.
    //   Atomic update is imp since __syncthread() will only synchronize threads
    //   in a given block, not across blocks.
    for (IndexType i = threadIdx.x; i < a.sizes[0]; i += blockDim.x) {
      const IndexType aOffset =
          detail::IndexToOffset<output_t, IndexType, ADims>::get(i, a);
      gpuAtomicAddNoReturn(&a.data[aOffset], smem[i]);
    }

  } else if (MemoryType == CUDAHistogramMemoryType::MULTI_BLOCK) {
    ////////////////////////// Multi Block memory //////////////////////////
    // atomically add to block specific global tensor
    // then atomically add to the global output tensor
    // compute histogram for the block
    FOR_KERNEL_LOOP(linearIndex, totalElements) {
      // Convert `linearIndex` into an offset of `b`
      const IndexType bOffset =
          detail::IndexToOffset<input_t, IndexType, BDims>::get(linearIndex, b);
      const auto bVal = b.data[bOffset];
      if (bVal >= minvalue && bVal <= maxvalue) {
        // Use value at `b` as an offset of `p`
        const IndexType bin =
            getBin<input_t, IndexType>(bVal, minvalue, maxvalue, nbins);
        const IndexType pIdx = p.strides[0] * blockIdx.x + bin;
        const IndexType pOffset =
            detail::IndexToOffset<output_t, IndexType, PDims>::get(pIdx, p);
        gpuAtomicAddNoReturn(&p.data[pOffset], getOp(linearIndex));
      }
    }
    __syncthreads();
    // NOTE: atomically update output bin count.
    //   Atomic update is imp since __syncthread() will only synchronize threads
    //   in a given block, not across blocks.
    const IndexType pIdx = p.strides[0] * blockIdx.x;
    const IndexType pOffset =
        detail::IndexToOffset<output_t, IndexType, PDims>::get(pIdx, p);
    for (IndexType i = threadIdx.x; i < a.sizes[0]; i += blockDim.x) {
      const IndexType aOffset =
          detail::IndexToOffset<output_t, IndexType, ADims>::get(i, a);
      gpuAtomicAddNoReturn(&a.data[aOffset], p.data[pOffset + i]);
    }

  } else {
    ////////////////////////// Global memory //////////////////////////
    // atomically add to the output tensor
    // compute histogram for the block
    FOR_KERNEL_LOOP(linearIndex, totalElements) {
      // Convert `linearIndex` into an offset of `b`
      const IndexType bOffset =
          detail::IndexToOffset<input_t, IndexType, BDims>::get(linearIndex, b);
      const auto bVal = b.data[bOffset];
      if (bVal >= minvalue && bVal <= maxvalue) {
        // Use value at `b` as an offset of `a`
        const IndexType bin =
            getBin<input_t, IndexType>(bVal, minvalue, maxvalue, nbins);
        const IndexType aOffset =
            detail::IndexToOffset<output_t, IndexType, ADims>::get(bin, a);
        gpuAtomicAddNoReturn(&a.data[aOffset], getOp(linearIndex));
      }
    }
  }
}
```

注意到在 KERNEL 函数中，程序根据内存类型是 `Shared Memory`,`Multi Block Memory` 还是 `Global Memory` 作了区分，不过算法是一致的。  
每个 Kernel 函数首先会创建一个本地的 `smem` 用于保存自己统计到的信息，然后在 `FOR_KERNEL_LOOP` 中枚举本 Kernel 分配到的数据部分，将其原子累加统计到自己的 `smem` 中。最后再将 `smem` 原子加到全局结果 `a` 中。

## Numpy
函数原型：

Numpy 中 `bincount` 函数是对其 C 语言版本 `arr_bincount` 函数的包装。代码如下。

```c
/*
 * arr_bincount is registered as bincount.
 *
 * bincount accepts one, two or three arguments. The first is an array of
 * non-negative integers The second, if present, is an array of weights,
 * which must be promotable to double. Call these arguments list and
 * weight. Both must be one-dimensional with len(weight) == len(list). If
 * weight is not present then bincount(list)[i] is the number of occurrences
 * of i in list.  If weight is present then bincount(self,list, weight)[i]
 * is the sum of all weight[j] where list [j] == i.  Self is not used.
 * The third argument, if present, is a minimum length desired for the
 * output array.
 */
NPY_NO_EXPORT PyObject *
arr_bincount(PyObject *NPY_UNUSED(self), PyObject *args, PyObject *kwds)
{
    PyObject *list = NULL, *weight = Py_None, *mlength = NULL;
    PyArrayObject *lst = NULL, *ans = NULL, *wts = NULL;
    npy_intp *numbers, *ians, len, mx, mn, ans_size;
    npy_intp minlength = 0;
    npy_intp i;
    double *weights , *dans;
    static char *kwlist[] = {"list", "weights", "minlength", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|OO:bincount",
                kwlist, &list, &weight, &mlength)) {
            goto fail;
    }

    lst = (PyArrayObject *)PyArray_ContiguousFromAny(list, NPY_INTP, 1, 1);
    if (lst == NULL) {
        goto fail;
    }
    len = PyArray_SIZE(lst);

    /*
     * This if/else if can be removed by changing the argspec to O|On above,
     * once we retire the deprecation
     */
    if (mlength == Py_None) {
        /* NumPy 1.14, 2017-06-01 */
        if (DEPRECATE("0 should be passed as minlength instead of None; "
                      "this will error in future.") < 0) {
            goto fail;
        }
    }
    else if (mlength != NULL) {
        minlength = PyArray_PyIntAsIntp(mlength);
        if (error_converting(minlength)) {
            goto fail;
        }
    }

    if (minlength < 0) {
        PyErr_SetString(PyExc_ValueError,
                        "'minlength' must not be negative");
        goto fail;
    }

    /* handle empty list */
    if (len == 0) {
        ans = (PyArrayObject *)PyArray_ZEROS(1, &minlength, NPY_INTP, 0);
        if (ans == NULL){
            goto fail;
        }
        Py_DECREF(lst);
        return (PyObject *)ans;
    }

    numbers = (npy_intp *)PyArray_DATA(lst);
    minmax(numbers, len, &mn, &mx);
    if (mn < 0) {
        PyErr_SetString(PyExc_ValueError,
                "'list' argument must have no negative elements");
        goto fail;
    }
    ans_size = mx + 1;
    if (mlength != Py_None) {
        if (ans_size < minlength) {
            ans_size = minlength;
        }
    }
    if (weight == Py_None) {
        ans = (PyArrayObject *)PyArray_ZEROS(1, &ans_size, NPY_INTP, 0);
        if (ans == NULL) {
            goto fail;
        }
        ians = (npy_intp *)PyArray_DATA(ans);
        NPY_BEGIN_ALLOW_THREADS;
        for (i = 0; i < len; i++)
            ians[numbers[i]] += 1;
        NPY_END_ALLOW_THREADS;
        Py_DECREF(lst);
    }
    else {
        wts = (PyArrayObject *)PyArray_ContiguousFromAny(
                                                weight, NPY_DOUBLE, 1, 1);
        if (wts == NULL) {
            goto fail;
        }
        weights = (double *)PyArray_DATA(wts);
        if (PyArray_SIZE(wts) != len) {
            PyErr_SetString(PyExc_ValueError,
                    "The weights and list don't have the same length.");
            goto fail;
        }
        ans = (PyArrayObject *)PyArray_ZEROS(1, &ans_size, NPY_DOUBLE, 0);
        if (ans == NULL) {
            goto fail;
        }
        dans = (double *)PyArray_DATA(ans);
        NPY_BEGIN_ALLOW_THREADS; // --------------------------这里开始统计--------------------------------
        for (i = 0; i < len; i++) {
            dans[numbers[i]] += weights[i];
        }
        NPY_END_ALLOW_THREADS;
        Py_DECREF(lst);
        Py_DECREF(wts);
    }
    return (PyObject *)ans;

fail:
    Py_XDECREF(lst);
    Py_XDECREF(wts);
    Py_XDECREF(ans);
    return NULL;
}
```

同样也是 for 的简单加法，允许多线程地进行累加。
