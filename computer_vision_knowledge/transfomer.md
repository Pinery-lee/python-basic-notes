# Transfomer

## 0. 问题背景

这里特指序列到序列的模型，基于Attention is all you need这篇论文。我想了解的是如何去工程化的设计模型。

## 1. 序列到序列的步骤

1. 文本序列分词
2. 分词序列编码
3. 整数编码序列词嵌入
4. **transformer模型**
5. 原始对数输出
6. 对数概率化
7. 整数编码序列
8. 解码为文本序列

> 有的模型类会将第3步词嵌入和第5-6步也放到模型实现中去。

## 2. `nn.Transfomer`的设计

如下所示，`torch 2.7.0`对于[`nn.Transfomer`](https://github.com/pytorch/pytorch/blob/v2.7.0/torch/nn/modules/transformer.py#L57)的设计是没有上面的第3、5和6步的。换句话说，`nn.Transfomer`只包含编码器和解码器。

![img](https://pic1.zhimg.com/80/v2-4d0a824d1015a388ed6fd92a3be26f7d_720w.webp?source=1def8aca)

### 2.1 [`nn.Transfomer`的参数](https://pytorch.ac.cn/docs/stable/generated/torch.nn.Transformer.html)

#### 2.1.1 实例化参数

实例化参数用于修改模型的架构或属性，为控制模型结构的超参数。

- **d_model** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 编码器/解码器输入中预期的特征数量（默认值=512，即词嵌入维度）。
- **nhead** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 多头注意力模型中的头数量（默认值=8）。
- **num_encoder_layers** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 编码器中的子编码器层数量（默认值=6）。
- **num_decoder_layers** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 解码器中的子解码器层数量（默认值=6）。
- **dim_feedforward** ([*int*](https://docs.pythonlang.cn/3/library/functions.html#int)) – 前馈网络模型的维度（默认值=2048，即mlp的中间维度）。

```python
        (linear1): Linear(in_features=512, out_features=2048, bias=True)
        (dropout): Dropout(p=0.1, inplace=False)
        (linear2): Linear(in_features=2048, out_features=512, bias=True)
```

- **dropout** ([*float*](https://docs.pythonlang.cn/3/library/functions.html#float)) – dropout 值（默认值=0.1）。
- **activation** ([*Union*](https://docs.pythonlang.cn/3/library/typing.html#typing.Union)*[*[*str*](https://docs.pythonlang.cn/3/library/stdtypes.html#str)*,* [*Callable*](https://docs.pythonlang.cn/3/library/typing.html#typing.Callable)*[**[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]**,* [*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]**]*) – 编码器/解码器中间层的激活函数，可以是字符串（“relu”或“gelu”）或一元可调用对象。默认值：relu
- **custom_encoder** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Any*](https://docs.pythonlang.cn/3/library/typing.html#typing.Any)*]*) – 自定义编码器（默认值=None）。
- **custom_decoder** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Any*](https://docs.pythonlang.cn/3/library/typing.html#typing.Any)*]*) – 自定义解码器（默认值=None）。
- **layer_norm_eps** ([*float*](https://docs.pythonlang.cn/3/library/functions.html#float)) – 层归一化组件中的 eps 值（默认值=1e-5,即 $\varepsilon$ ：[**防止分母为零的非常小常数**](./layernorm.md)）。
- **batch_first** ([*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)) – 如果为 `True`，则输入和输出张量的形状为 (batch, seq, feature)。默认值：`False` (seq, batch, feature)。
- **norm_first** ([*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)) – 如果为 `True`，编码器和解码器层将在其他注意力层和前馈操作之前执行 LayerNorm，否则在其后执行。默认值：`False` (之后)。
- **bias** ([*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)) – 如果设置为 `False`，`Linear` 和 `LayerNorm` 层将不会学习加性偏置。默认值：`True`。

使用默认的参数构建的Transformer模型

```python
nn.Transformer()
```

```python
Transformer(
  (encoder): TransformerEncoder(
    (layers): ModuleList(
      (0-5): 6 x TransformerEncoderLayer(
        (self_attn): MultiheadAttention(
          (out_proj): NonDynamicallyQuantizableLinear(in_features=512, out_features=512, bias=True)
        )
        (linear1): Linear(in_features=512, out_features=2048, bias=True)
        (dropout): Dropout(p=0.1, inplace=False)
        (linear2): Linear(in_features=2048, out_features=512, bias=True)
        (norm1): LayerNorm((512,), eps=1e-05, elementwise_affine=True)
        (norm2): LayerNorm((512,), eps=1e-05, elementwise_affine=True)
        (dropout1): Dropout(p=0.1, inplace=False)
        (dropout2): Dropout(p=0.1, inplace=False)
      )
    )
    (norm): LayerNorm((512,), eps=1e-05, elementwise_affine=True)
  )
  (decoder): TransformerDecoder(
    (layers): ModuleList(
      (0-5): 6 x TransformerDecoderLayer(
        (self_attn): MultiheadAttention(
          (out_proj): NonDynamicallyQuantizableLinear(in_features=512, out_features=512, bias=True)
        )
        (multihead_attn): MultiheadAttention(
          (out_proj): NonDynamicallyQuantizableLinear(in_features=512, out_features=512, bias=True)
        )
        (linear1): Linear(in_features=512, out_features=2048, bias=True)
        (dropout): Dropout(p=0.1, inplace=False)
        (linear2): Linear(in_features=2048, out_features=512, bias=True)
        (norm1): LayerNorm((512,), eps=1e-05, elementwise_affine=True)
        (norm2): LayerNorm((512,), eps=1e-05, elementwise_affine=True)
        (norm3): LayerNorm((512,), eps=1e-05, elementwise_affine=True)
        (dropout1): Dropout(p=0.1, inplace=False)
        (dropout2): Dropout(p=0.1, inplace=False)
        (dropout3): Dropout(p=0.1, inplace=False)
      )
    )
    (norm): LayerNorm((512,), eps=1e-05, elementwise_affine=True)
  )
)
```

#### 2.1.2 输入参数

输入参数控制模型每次输入的数据及其行为，在训练或推理时传入。

- **src** ([*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)) – 编码器输入的序列（必需）。
- **tgt** ([*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)) – 解码器输入的序列（必需）。因为是序列生成模型，目标序列（右移一位），喂给 decoder，**帮助模型一步步生成目标序列**，是必须的。
- **src_mask** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]*) – src 序列的加性掩码（可选）。
- **tgt_mask** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]*) – tgt 序列的加性掩码（可选）。
- **memory_mask** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]*) – 编码器输出的加性掩码（可选）。
- **src_key_padding_mask** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]*) – src 键的张量掩码，按批次划分（可选）。
- **tgt_key_padding_mask** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]*) – tgt 键的张量掩码，按批次划分（可选）。
- **memory_key_padding_mask** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*Tensor*](https://pytorch.ac.cn/docs/stable/tensors.html#torch.Tensor)*]*) – memory 键的张量掩码，按批次划分（可选）。
- **src_is_causal** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)*]*) – 如果指定，则将因果掩码应用为 `src_mask`。默认值：`None`；尝试检测因果掩码。警告：`src_is_causal` 提供了一个提示，表明 `src_mask` 是因果掩码。提供不正确的提示可能导致执行错误，包括前向和后向兼容性问题。在 decoder 里，每个位置的 token **只能看到前面的内容**，不能偷看未来的信息（即 “因果关系”）。
- **tgt_is_causal** ([*Optional*](https://docs.pythonlang.cn/3/library/typing.html#typing.Optional)*[*[*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)*]*) – 如果指定，则将因果掩码应用为 `tgt_mask`。默认值：`None`；尝试检测因果掩码。警告：`tgt_is_causal` 提供了一个提示，表明 `tgt_mask` 是因果掩码。提供不正确的提示可能导致执行错误，包括前向和后向兼容性问题。
- **memory_is_causal** ([*bool*](https://docs.pythonlang.cn/3/library/functions.html#bool)) – 如果指定，则将因果掩码应用为 `memory_mask`。默认值：`False`。警告：`memory_is_causal` 提供了一个提示，表明 `memory_mask` 是因果掩码。提供不正确的提示可能导致执行错误，包括前向和后向兼容性问题。

> 需要注意的是：1. memory指的是encoder的输出，一般只对tgt而不对src和memory进行因果掩膜，所以src_mask、memory_mask不常用，常用的是tgt_mask。2. 还需要对<pad>进行掩膜，一般来说会对tgt和src的<pad>进行掩膜，不对memory进行掩膜，所以memory_key_padding_mask不常用，常用的是src_key_padding_mask和tgt_key_padding_mask。3. tgt_is_causal控制的是用户对自己的输入因果掩膜是否确定，None会检测掩码，最好使用None即默认参数。

| 序号 | tgt_is_causal  | tgt_mask       | 结果                                                        |
| ---- | -------------- | -------------- | ----------------------------------------------------------- |
| 1    | None或者不提供 | None或者不提供 | 内部自动确定为不对tgt做因果掩膜 等于7                       |
| 2    | None或者不提供 | 为下三角矩阵   | 内部自动确定为正确的掩膜格式，对tgt做因果以掩膜 等于5 等于8 |
| 3    | None或者不提供 | 不为下三角矩阵 | 内部自动检测为错的掩膜格式，对tgt做非因果掩膜 等于9         |
| 4    | True           | None或者不提供 | 报错                                                        |
| 5    | True           | 为下三角矩阵   | 不自动检测，对tgt做因果掩膜 等于2 等于8                     |
| 6    | True           | 不为下三角矩阵 | 不可预测                                                    |
| 7    | False          | None或者不提供 | 不自动检测，不对tgt做因果掩膜 等于1                         |
| 8    | False          | 为下三角矩阵   | 不自动检测，对tgt做因果掩膜 等于2 等于5                     |
| 9    | False          | 不为下三角矩阵 | 不自动检测，对tgt做非因果掩膜 等于3                         |
|      |                |                |                                                             |

> 想要模型正确因果掩膜，使用2、5、8，关键在于要提供正确的因果掩膜，推荐使用`nn.Transformer`的`generate_square_subsequent_mask()`方法

[详细的参数解释请看这里](https://www.zhihu.com/question/584772471)

#### 2.1.3 形状变化

忽略掉非批次的情况，*S* 是源序列长度，*T* 是目标序列长度，*N* 是批次大小，*E* 是特征数量

- src: 如果 batch_first=False 则为 (*S*,*N*,*E*)，如果 batch_first=True 则为 (*N*, *S*, *E*)。
- tgt:如果 batch_first=False 则为 (*T*,*N*,*E*)，如果 batch_first=True 则为 (*N*, *T*, *E*)。
- src_mask:(*S*,*S*) 或(*N*⋅num_heads,*S*,*S*)。
- tgt_mask: (*T*,*T*) 或 (*N*⋅num_heads,*T*,*T*)。
- memory_mask: (*T*,*S*)。
- src_key_padding_mask: 对于非批次输入为(*S*)，否则为(*N*,*S*)。
- tgt_key_padding_mask: 对于非批次输入为(*T*)，否则为(*N*,*T*)。
- memory_key_padding_mask: 对于非批次输入为(*S*)，否则为(*N*,*S*)。

### 2.2 模块化设计

`transformer.py`作为整个模型实现的载体主入口，其中提供了5个类给用户

```python
__all__ = [
    "Transformer",
    "TransformerEncoder",
    "TransformerDecoder",
    "TransformerEncoderLayer",
    "TransformerDecoderLayer",
]
```

```python
nn.Transformer
--nn.TransformerEncoder
----nn.TransformerEncoderLayer × N
--nn.TransformerDecoder
----nn.TransformerDecoderLayer × N
```

![img](https://picx.zhimg.com/80/v2-a1275ba58e76c78680a9c536526c1376_720w.webp?source=1def8aca)

#### 2.2.1 `nn.TransformerEncoder`

编码器的输入是源序列，输出是memory：

- 源序列形状： (*N*, *S*, *E*) 默认 batch_first=True
- memory形状： (*N*, *S*, *E*) 

使用：

```python
import torch
import torch.nn as nn
encoder_layer = nn.TransformerEncoderLayer(d_model=512, nhead=8,batch_first=True)
transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=6)
src = torch.rand(10, 32, 512)
out = transformer_encoder(src)
out.shape
```

```python
torch.Size([10, 32, 512])
```

由N个`nn.TransformerEncoderLayer`连接而成，连接方式是串联，并无残差连接：

```python
for mod in self.layers:
            output = mod(
                output,
                src_mask=mask,
                is_causal=is_causal,
                src_key_padding_mask=src_key_padding_mask_for_layers,
            )
```

#### 2.2.2 `nn.TransformerDecoder`

解码器相比于编码器要复杂，原因在于要在此处实现序列的循环生成

解码器的输入是 (因果掩膜后的目标序列，memory)， 输出是结果序列

- 因果掩膜后的目标序列形状： (*N*, *T*, *E*)
- memory形状：(*N*, *S*, *E*) 
- 结果序列形状： (*N*, *T*, *E*)

```python
decoder_layer = nn.TransformerDecoderLayer(d_model=512, nhead=8, batch_first=True)
transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)
memory = torch.rand(32, 10, 512)
tgt = torch.rand(32, 20, 512)
out = transformer_decoder(tgt, memory)
out.shape
```

```python
torch.Size([32, 20, 512])
```

由N个`nn.TransformerDecoderLayer`连接而成，连接方式不是单纯的串联，如下所示，memory会进入每一个`nn.TransformerDecoderLayer`

```python
    for mod in self.layers:
        output = mod(
            output,
            memory,
            tgt_mask=tgt_mask,
            memory_mask=memory_mask,
            tgt_key_padding_mask=tgt_key_padding_mask,
            memory_key_padding_mask=memory_key_padding_mask,
            tgt_is_causal=tgt_is_causal,
            memory_is_causal=memory_is_causal,
        )
```

![img](https://pic3.zhimg.com/v2-3a752f82f2414c4a49f377440eb888bc_1440w.jpg)

#### 2.2.3 `nn.TransformerEncoderLayer`

`TransformerEncoderLayer` 包括两个主要模块：

- **多头自注意力层（Self-Attention）**
- **前馈神经网络（Feed-Forward Network）**

每个模块后面都接了 **残差连接 + LayerNorm**

#### 2.2.4 `nn.TransformerDecoderLayer`

每个 `TransformerDecoderLayer` 包括三个主要部分：

1. **Masked Self-Attention（自注意力）子层**
   - 输入：目标序列 `tgt`
   - 用于捕捉当前目标序列中的上下文依赖关系。
   - 使用 `MultiheadAttention` 实现，支持 mask 和 padding mask。
2. **Cross-Attention（交叉注意力）子层**
   - 输入：`tgt`（作为查询）和 `memory`（从编码器得到的表示）
   - 用于对编码器输出进行关注，从而融合上下文信息。
3. **Feedforward 网络（前馈全连接网络）**
   - 两个线性层和一个激活函数（如 ReLU 或 GELU），加 Dropout。
   - 输入维度为 `d_model`，中间层为 `dim_feedforward`，输出维度为 `d_model`。

| 模块 | 名称                      | 查询（Q）      | 键值（K/V）                | 作用                                       |
| ---- | ------------------------- | -------------- | -------------------------- | ------------------------------------------ |
| 1️⃣    | **Masked Self-Attention** | 当前生成的序列 | 当前生成的序列             | 理解上下文历史(只看自己历史)，但不能看未来 |
| 2️⃣    | **Cross Attention**       | 当前生成的序列 | 编码器输出（源序列的表示） | 融合输入序列信息（源语言/上下文）          |

每个模块后面都接了 **残差连接 + LayerNorm**

更深入的讲解请看[The Illustrated Transformer – Jay Alammar – Visualizing machine learning one concept at a time.](https://jalammar.github.io/illustrated-transformer/)

## 3. 使用实例

[mytransformer/Transfomer_demo.ipynb at main · Pinery-lee/mytransformer](https://github.com/Pinery-lee/mytransformer/blob/main/Transfomer_demo.ipynb)