# Self-attention 和 Multi-head attention

## 0. 问题背景

随着计算机视觉中transformer模型所占的比例越来越高，以及火热的多模态模型，基于transformer的视觉模型与基于cnn的模型呈现分庭抗礼的态势。所以从[Attention Is All You Need](https://yiyibooks.cn/yiyibooks/Attention_Is_All_You_Need/index.html)该文中学习自注意力机制和多头注意力机制成了cv从业者的基本功。该文使用自注意力的动机在于：传统基于RNN或者CNN的模型在学习远距离依赖时(大的卷积核或者更多层)计算代价较高，Transformer 通过 self-attention 将其降低为常数复杂度，但引入了平均模糊（因为 attention 实质上是一个加权平均（weighted sum）操作，可能会导致信息“模糊化”。如果 attention 把注意力分配得过于平均，重要的信息可能会被其他不相关位置“稀释”。）的问题，这一问题可以用 Multi-Head Attention 来缓解。

## 1. 自注意力

自注意力，又称为缩放点积注意力机制，是应用最广泛的的注意力机制。

> 动机：自注意力提出的动机是为了减轻或者消除自然语言处理中RNN模型的并行化和长程依赖问题。

对比：

| **特性**         | **自注意力 (Self-Attention)**    | **RNN**                        | **CNN**                      |
| ---------------- | -------------------------------- | ------------------------------ | ---------------------------- |
| **依赖关系建模** | 全局依赖（任意位置间直接交互）   | 局部依赖（仅历史信息逐步传递） | 局部依赖（固定窗口内交互）   |
| **并行化能力**   | 完全并行（矩阵运算）             | 序列依赖，难以并行             | 部分并行（窗口内可并行）     |
| **长程依赖处理** | 天然支持长程依赖（无衰减）       | 梯度消失/爆炸问题严重          | 需堆叠多层扩大感受野         |
| **计算复杂度**   | $O(n^2)$ （序列长度 \(n\)）      | $O(n)$ （时间步计算）          | $O(k \cdot n)$ （核大小k）   |
| **参数共享**     | 无位置参数共享（但多头共享权重） | 时间步共享权重                 | 空间位置共享卷积核           |
| **典型应用场景** | Transformer、BERT、GPT           | 语言模型、时间序列预测         | 图像分类、文本分类（1D卷积） |

### 1.1 理论公式


$$
\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$


-   $(Q, K, V)$ 为查询Query、键Key、值Value矩阵， $ \sqrt{d_k} $ 为缩放因子， $d_k$ 是Key的维度。
-   $(Q, K, V)$ 表示每个 token 的 Query“要关注什么”、Key“匹配什么”，和 Value“输出什么”，由于 $(Q, K, V)$ **都是来自于输入**，所以叫**自注意力**机制
-  第一步通过**点积**计算注意力得分（attention score）：点积 $QK^T$ 就是计算 $Q$ 和 $K$ 的相似度。
-  第二步将注意力得分进行**缩放**和**归一化**：缩放就是除以 $\sqrt{d_k}$ , 归一化就是使用 $softmax$ ，得到注意力权重（attention weight)。这也是缩放点积注意力名称的来源。
-  第三步使用注意力权重对 $V$ 进行加权，得到输出。

### 1.2 为什么需要QKV?

**我们需要 QKV（Query、Key、Value）机制，而不是直接学习注意力权重，是为了让注意力具有**：
 ✅ 可泛化性、✅ 动态性、✅ 计算效率高、✅ 支持长序列、✅ 参数量小。

####  1.2.1 如果**直接学习注意力权重**会怎么样？

- 这意味着你要**为每个 token 学一个权重值**
- 权重是固定的，跟输入内容无关
- 对不同输入样本只能使用**同一套注意力连接** → 不能泛化
- 参数量巨大，不支持变化长度的序列
- 这本质上是：一个 **超大的全连接层或卷积核**

####  1.2.2 使用 QKV 的自注意力是怎么做的？

核心思路： $Q = XW_q^T+B, K = XW_k^T+B, V = XW_v^T+B$  → QKV 是从输入通过线性变换动态生成的！

```python
self.query = nn.Linear(self.hidden_size, self.all_head_size, bias=config.qkv_bias)
self.key = nn.Linear(self.hidden_size, self.all_head_size, bias=config.qkv_bias)
self.value = nn.Linear(self.hidden_size, self.all_head_size, bias=config.qkv_bias)
```

> ✅ **在训练中，模型真正学习的参数是生成 Q、K、V 的权重矩阵** —— 即  $ W_q, W_k, W_v$ ，而不是注意力权重本身。注意力权重并不是直接学得的参数，而是通过输入计算出来的中间结果。

| 名称                | 参数性质   | 说明                                 |
| ------------------- | ---------- | ------------------------------------ |
| `W_Q`               | ✅ 可学习   | 把输入投影成 Query 空间              |
| `W_K`               | ✅ 可学习   | 把输入投影成 Key 空间                |
| `W_V`               | ✅ 可学习   | 把输入投影成 Value 空间              |
| `attention_weights` | ❌ 不是参数 | 是由 Q 和 K 计算出来的内容相关性结果 |

使用QKV计算注意力权重的好处：

| 特性             | QKV自注意力                       |
| ---------------- | --------------------------------- |
| **动态性**       | Q、K、V 是每个输入动态生成的      |
| **可泛化性**     | 同一套参数 W_q/k/v 可用于不同输入 |
| **参数量小**     | 只需学习 W_q/k/v（3 × d×d）       |
| **支持变长输入** | $QK^T$  自动适配不同序列长度      |
| **内容感知性**   | 不同输入产生不同注意力矩阵        |

#### 1.2.3 举例说明

假设你正在看一句话：“**The cat sat on the mat.**”

使用 QKV：

- 每个词（token）先生成一个 Query、Key、Value 向量
- Query 和所有 Key 点积，得到每个词对当前词的重要程度
- 再用这些权重加权 Value，得到当前词的语义表示

每次输入内容变了，Q、K、V 都变了，注意力权重也会跟着变。这是“**内容感知的连接权重**”。

#### 1.2.4 简要总结

| 问题                          | 回答简要说明                               |
| ----------------------------- | ------------------------------------------ |
| 为什么不用直接学习权重？      | 会固定、无法泛化、参数太多、输入不能变     |
| QKV 有什么用？                | 提供动态权重、支持变长输入、参数少、可泛化 |
| 是不是 QKV 最后也会变成权重？ | 是，但这些权重是**输入驱动、内容感知的**   |

### 1.3 为什么要除以 $\sqrt{d_k}$ ？

总结一句话：缩放是可以使得注意力分数即点积结果不至于很大，这样经过softmax归一化后不会倾向于其中最大的元素接近1，其余全是0的分布，这种分布会导致梯度消失。详细讲解可以看[这里](https://zhuanlan.zhihu.com/p/695762892?share_code=w1h4U3lhaCOa&utm_psn=1903852051466785745)

除以标准差 $\sqrt{d_k}$ ，就是为了把点积结果的方差变为1（类似于普通正态分布变为标准正态分布，不过期望为0）,实验一下：

```python
import torch
import numpy as np

# 设置随机种子以确保可重复性
torch.manual_seed(0)

# 设置向量维度和样本数量
d_k = 64
num_samples = 100000

# 生成多个查询向量和键向量
queries = torch.randn(num_samples, d_k)  # 形状: (num_samples, d_k)
keys = torch.randn(num_samples, d_k)     # 形状: (num_samples, d_k)

# 计算每一对查询向量和键向量的点积
dot_products = torch.sum(queries * keys, dim=1)  # 形状: (num_samples,)

# 计算点积的方差（总体方差）
variance1 = torch.var(dot_products / np.sqrt(d_k), unbiased=False)
variance2 = torch.var(dot_products , unbiased=False)

print(f"缩放后点积的方差（大样本量）: {variance1}")
print(f"缩放前点积的方差（大样本量）: {variance2}")
```

输出：

```python
缩放后点积的方差（大样本量）: 0.997921884059906
缩放前点积的方差（大样本量）: 63.867000579833984
```

### 1.4 为什么要用softmax归一化？

> 因为我们希望注意力权重是**概率分布**，也就是说：每个 token 对其他 token 的关注度是非负的，总和为 1，这样就能进行**加权平均**，而不是任意放大或缩小。

#### 1.4.1  **将任意的打分变成概率**

点积只是一个分数，没有界限，可以正也可以负。
 如果不归一化，值可以很大、很小甚至负数，不适合当作“权重”。

> softmax 把这些 raw scores 转换为 [0,1][0, 1] 的概率，总和为 1
>  → 便于我们对 value 向量做加权平均。

------

#### 1.4.2 可解释性：归一化之后就能解释“关注多少”

softmax 后的注意力权重 $\alpha_{ij}$ 可以直接解释为：

- “第 i 个 token 对第 j 个 token 的注意力有多少”
- 所以可视化时你会看到注意力热力图（Attention Heatmap），也都是基于这个 softmax 权重

------

#### 1.4.3  **便于梯度传播**

softmax 有平滑特性，避免了 hard selection（比如 argmax 那种不可导操作）
 可以让模型学会“更关注谁”而不是“只关注谁”

------

#### 1.4.4 **归一化后，值不会爆炸，有利于训练稳定**

如果直接用未归一化的打分来加权 value，容易出现数值不稳定、梯度爆炸或消失

------

🧠 举个例子：

假设一个 token 对其他 3 个 token 的打分是：

[2.3, 9.1, 0.5]

如果直接拿这个向量做权重来加权 value，结果难以解释，且不一定稳定。
 但 softmax 后：

$softmax([2.3,9.1,0.5])≈[0.002, 0.995, 0.003]\text{softmax}([2.3, 9.1, 0.5]) \approx [0.002,\ 0.995,\ 0.003]$

这个就可以表示为：“我几乎全部注意力都给了第 2 个 token”，可解释、稳定、可训练。

------

✅ 总结一句话：

> **归一化是为了让注意力权重变成概率分布**，从而便于模型学习、解释和稳定地加权 value 值。

---

### 1.5 实现

#### 1.5.1 伪代码

- 伪代码用于表示核心的精简流程

- `@`表示矩阵乘法，适用于`torch.tensor`, 等价于`torch.matmul(a, b)`

```python
# 输入：X ∈ ℝ^(L×d)
Q = X @ W_Q    # W_Q ∈ ℝ^(d×d)
K = X @ W_K
V = X @ W_V
# 注意力得分：
attention_scores = Q @ K.T / sqrt(d)
# 注意力权重：
attention_weights = softmax(attention_scores, dim=-1)
# 最终输出：
output = attention_weights @ V
```

#### 1.5.2 原生实现

- 原生实现可以跑通，但没有多余优化， $QKV$ 也都是随机的而不是由输入线性变化得到的。
- 已经将公式全部实现

```python
# 导入库
import torch
import torch.nn.functional as F

# 示例输入序列
input_sequence = torch.tensor([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9],[0.5, 0.2, 0.4]])

# 生成 Key、Query 和 Value 矩阵的随机权重
random_weights_key = torch.randn(input_sequence.size(-1), input_sequence.size(-1))
random_weights_query = torch.randn(input_sequence.size(-1), input_sequence.size(-1))
random_weights_value = torch.randn(input_sequence.size(-1), input_sequence.size(-1))

# 计算 Key、Query 和 Value 矩阵
key = torch.matmul(input_sequence, random_weights_key)
query = torch.matmul(input_sequence, random_weights_query)
value = torch.matmul(input_sequence, random_weights_value)

# 计算注意力分数
attention_scores = torch.matmul(query, key.T) / torch.sqrt(torch.tensor(query.size(-1), dtype=torch.float32))

# 使用 softmax 函数获得注意力权重
attention_weights = F.softmax(attention_scores, dim=-1)

# 计算 Value 向量的加权和
output = torch.matmul(attention_weights, value)

print("自注意力机制后的输出:")
print(output)
```

✅ 非常易于理解和教学演示。

❌ 没有支持 `mask`，无法用于 NLP 中常见的 padding 或 causal。

❌ 没有 dropout。

❌ 无法处理 batched 输入。

❌ 没有 GQA、多头注意力、分块计算等高级功能。

❌ 没有区分训练/推理模式（比如 dropout）。

#### 1.5.3 工程级别实现

实现一：[adore801120/attention-is-all-you-need-pytorch](https://github.com/jadore801120/attention-is-all-you-need-pytorch/blob/master/transformer/Modules.py#L7)

```python
class ScaledDotProductAttention(nn.Module):
    ''' Scaled Dot-Product Attention '''

    def __init__(self, temperature, attn_dropout=0.1):
        super().__init__()
        # 缩放因子
        self.temperature = temperature
        # 加入了正则化
        self.dropout = nn.Dropout(attn_dropout)

    def forward(self, q, k, v, mask=None):

        attn = torch.matmul(q / self.temperature, k.transpose(2, 3))
	    # 将mask中为0的地方的值替换为-1e9，这样在softmax的时候-1e9会变为0
        if mask is not None:
            attn = attn.masked_fill(mask == 0, -1e9)
        # 对注意力权重应用dropout
        attn = self.dropout(F.softmax(attn, dim=-1))
        output = torch.matmul(attn, v)

        return output, attn
```

| 优化点      | 说明                                                         |
| ----------- | ------------------------------------------------------------ |
| 🎯 模块化    | 封装成 PyTorch 的 `nn.Module`，便于复用和组合到 Transformer 模块中 |
| 🎯 支持 mask | 加入 `masked_fill(mask == 0, -1e9)`，可用于 padding 和 causal mask |
| 🎯 Dropout   | 增加随机性，避免过拟合                                       |

➡️ 适合构建自定义 Transformer 模型，用于中等规模任务。

实现二：[torch.nn.functional.scaled_dot_product_attention — PyTorch 2.7 documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html#torch.nn.functional.scaled_dot_product_attention)

```python
# Efficient implementation equivalent to the following:
def scaled_dot_product_attention(query, key, value, attn_mask=None, dropout_p=0.0,
        is_causal=False, scale=None, enable_gqa=False) -> torch.Tensor:
    # 提取 Query 和 Key 张量的长度维度，用于后续构建注意力矩阵和 Mask
    L, S = query.size(-2), key.size(-2)
    # 支持默认，也支持自定缩放因子
    scale_factor = 1 / math.sqrt(query.size(-1)) if scale is None else scale
    # 支持bias
    attn_bias = torch.zeros(L, S, dtype=query.dtype, device=query.device)
    # 因果遮挡。
    # 在训练语言模型时，每个位置只能看到自己以及之前的 token，不能“偷看未来”。所以要构造一个下三角矩阵（tril()），把上三角部分填成 -inf（经过 softmax 后接近 0），注意力置为0。
    if is_causal:
        assert attn_mask is None
        temp_mask = torch.ones(L, S, dtype=torch.bool).tril(diagonal=0)
        attn_bias.masked_fill_(temp_mask.logical_not(), float("-inf"))
        attn_bias.to(query.dtype)
	# 允许自定义mask
    if attn_mask is not None:
        if attn_mask.dtype == torch.bool:
            attn_bias.masked_fill_(attn_mask.logical_not(), float("-inf"))
        else:
            attn_bias = attn_mask + attn_bias
	# 支持分组查询注意力Grouped Query Attention（GQA）
    # GQA 让你用更少的 Key/Value 组去服务更多的 Query，比如：Query 是 16 个头，Key/Value 只有 4 个头，就通过 repeat_interleave 复制 Key/Value 来适配 Query，这样可以 减少计算量与内存，但保留大容量 Query 的灵活性。
    if enable_gqa:
        key = key.repeat_interleave(query.size(-3)//key.size(-3), -3)
        value = value.repeat_interleave(query.size(-3)//value.size(-3), -3)

    attn_weight = query @ key.transpose(-2, -1) * scale_factor
    attn_weight += attn_bias
    attn_weight = torch.softmax(attn_weight, dim=-1)
    # 只有training的时候才dropout
    attn_weight = torch.dropout(attn_weight, dropout_p, train=True)
    return attn_weight @ value
```



## 2. 多头注意力

“多头注意力”这个概念是**结构形式**，它描述的是：

> 把注意力机制并行分成多个“头”，每个头使用不同的参数来提取不同的信息，然后再把多个头的输出拼接起来。

> 所以：**“多头”是方式，“注意力类型”是内容。**

所以可以有：

- 多头的**自注意力**
- 多头的**交叉注意力**
- 多头的**局部注意力**
- 多头的**因果注意力**

每个头都可以独立处理不同信息，但它们遵循同一个注意力规则（比如都用自注意力）

> 注意力之于多头注意力，好似单卷积核之于多卷积核。

### 2.1 多头注意力的核心思想

- Q/K/V 被拆成 n 块，n个头**在不同的子空间中建模注意力**，这样多个头就能从多个方向理解信息。
- 再把多个头得到的注意力拼接回去。
- 最后通过一个线性投影层融合和还原维度。

### 2.2 实现

#### 2.2.1 伪代码

```python
# 输入:
# X: 输入张量，形状为 (batch_size, seq_len, embed_dim)
# n_heads: 注意力头数
# d_k: 每个头的 Query / Key 的维度
# d_v: 每个头的 Value 的维度
# W_q, W_k, W_v: 投影矩阵，形状为 (embed_dim, n_heads * d_k) / (embed_dim, n_heads * d_v)
# W_o: 输出投影矩阵，形状为 (n_heads * d_v, embed_dim)

# Step 1: 线性映射，生成 Q, K, V
Q = X @ W_q  # shape: (B, L, n_heads * d_k)
K = X @ W_k
V = X @ W_v

# Step 2: 拆分多头
Q = reshape(Q, shape=(B, L, n_heads, d_k)).transpose(1, 2)  # (B, n_heads, L, d_k)
K = reshape(K, shape=(B, L, n_heads, d_k)).transpose(1, 2)
V = reshape(V, shape=(B, L, n_heads, d_v)).transpose(1, 2)

# Step 3: 对每个头计算注意力
scores = (Q @ K.transpose(-2, -1)) / sqrt(d_k)  # (B, n_heads, L, L)
attn_weights = softmax(scores, dim=-1)
attn_output = attn_weights @ V  # (B, n_heads, L, d_v)

# Step 4: 合并所有头
attn_output = attn_output.transpose(1, 2).reshape(B, L, n_heads * d_v)

# Step 5: 输出线性映射
output = attn_output @ W_o  # (B, L, embed_dim)

```

#### 2.2.2 原生实现

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# 定义一个 MultiHeadAttention 类，它继承自 nn.Module
class MultiHeadAttention(nn.Module):
    def __init__(self, heads, d_model, dropout=0.1):
        # 调用父类的构造函数
        super().__init__()
        # 保存模型维度和头数
        self.d_model = d_model
        self.d_k = d_model // heads  # 每个头对应的维度
        self.h = heads  # 头的数量

        # 初始化线性层，用于将输入转换为查询（Q）、键（K）和值（V）
        self.q_linear = nn.Linear(d_model, d_model)
        self.k_linear = nn.Linear(d_model, d_model)
        self.v_linear = nn.Linear(d_model, d_model)
        # 初始化Dropout层，用于正则化
        self.dropout = nn.Dropout(dropout)
        # 初始化输出线性层，用于将多头注意力输出转换为模型维度
        self.out = nn.Linear(d_model, d_model)

    # 定义注意力机制的计算过程
    def attention(self, q, k, v, mask=None):
        # 计算Q和K的矩阵乘积，然后除以根号下d_k
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)
        # 如果提供了掩码，则将掩码对应的位置设置为负无穷，这样在softmax后这些位置的值为0
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        # 应用softmax函数获得注意力权重
        scores = F.softmax(scores, dim=-1)
        # 应用dropout
        scores = self.dropout(scores)
        # 将注意力权重和V相乘得到输出
        output = torch.matmul(scores, v)
        return output

    # 定义前向传播过程
    def forward(self, q, k, v, mask=None):
        batch_size = q.size(0)
        # 将输入Q、K、V通过线性层，并调整形状以进行多头注意力计算
        q = self.q_linear(q).view(batch_size, -1, self.h, self.d_k).transpose(1, 2)
        k = self.k_linear(k).view(batch_size, -1, self.h, self.d_k).transpose(1, 2)
        v = self.v_linear(v).view(batch_size, -1, self.h, self.d_k).transpose(1, 2)
        # 计算注意力输出
        scores = self.attention(q, k, v, mask)
        # 将多头输出合并，并调整形状以匹配模型维度
        concat = scores.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        # 通过输出线性层
        output = self.out(concat)
        return output
```

#### 2.2.3 工程级别实现

实现一：[jadore801120/attention-is-all-you-need-pytorch](https://github.com/jadore801120/attention-is-all-you-need-pytorch/blob/master/transformer/SubLayers.py#L9)

```python
class MultiHeadAttention(nn.Module):
    ''' Multi-Head Attention module '''

    def __init__(self, n_head, d_model, d_k, d_v, dropout=0.1):
        super().__init__()
        # d_model 就是嵌入维度（embedding dimension），也叫做模型的隐状态维度（hidden size），是 Transformer 中贯穿始终的核心维度。

        self.n_head = n_head
        self.d_k = d_k
        self.d_v = d_v

        self.w_qs = nn.Linear(d_model, n_head * d_k, bias=False) # Q要和K点积，所以其实必须d_q = d_k
        self.w_ks = nn.Linear(d_model, n_head * d_k, bias=False)
        self.w_vs = nn.Linear(d_model, n_head * d_v, bias=False)
        self.fc = nn.Linear(n_head * d_v, d_model, bias=False)

        self.attention = ScaledDotProductAttention(temperature=d_k ** 0.5)

        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model, eps=1e-6)


    def forward(self, q, k, v, mask=None):

        d_k, d_v, n_head = self.d_k, self.d_v, self.n_head
        sz_b, len_q, len_k, len_v = q.size(0), q.size(1), k.size(1), v.size(1)

        residual = q

        # Pass through the pre-attention projection: b x lq x (n*dv)
        # Separate different heads: b x lq x n x dv
        q = self.w_qs(q).view(sz_b, len_q, n_head, d_k)
        k = self.w_ks(k).view(sz_b, len_k, n_head, d_k)
        v = self.w_vs(v).view(sz_b, len_v, n_head, d_v)

        # Transpose for attention dot product: b x n x lq x dv
        q, k, v = q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)

        if mask is not None:
            mask = mask.unsqueeze(1)   # For head axis broadcasting.

        q, attn = self.attention(q, k, v, mask=mask)

        # Transpose to move the head dimension back: b x lq x n x dv
        # Combine the last two dimensions to concatenate all the heads together: b x lq x (n*dv)
        q = q.transpose(1, 2).contiguous().view(sz_b, len_q, -1)
        q = self.dropout(self.fc(q))
        q += residual

        q = self.layer_norm(q)

        return q, attn
```

实现二：[PyTorch Tutorials 2.7.0+cu126 documentation](https://docs.pytorch.org/tutorials/intermediate/transformer_building_blocks.html#)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    """
    Computes multi-head attention. Supports nested or padded tensors.

    Args:
        E_q (int): Size of embedding dim for query
        E_k (int): Size of embedding dim for key
        E_v (int): Size of embedding dim for value
        E_total (int): Total embedding dim of combined heads post input projection. Each head
            has dim E_total // nheads
        nheads (int): Number of heads
        dropout (float, optional): Dropout probability. Default: 0.0
        bias (bool, optional): Whether to add bias to input projection. Default: True
    """

    def __init__(
        self,
        E_q: int,
        E_k: int,
        E_v: int,
        E_total: int,
        nheads: int,
        dropout: float = 0.0,
        bias=True,
        device=None,
        dtype=None,
    ):
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.nheads = nheads
        self.dropout = dropout
        self._qkv_same_embed_dim = E_q == E_k and E_q == E_v
        if self._qkv_same_embed_dim:
            self.packed_proj = nn.Linear(E_q, E_total * 3, bias=bias, **factory_kwargs)
        else:
            self.q_proj = nn.Linear(E_q, E_total, bias=bias, **factory_kwargs)
            self.k_proj = nn.Linear(E_k, E_total, bias=bias, **factory_kwargs)
            self.v_proj = nn.Linear(E_v, E_total, bias=bias, **factory_kwargs)
        E_out = E_q
        self.out_proj = nn.Linear(E_total, E_out, bias=bias, **factory_kwargs)
        assert E_total % nheads == 0, "Embedding dim is not divisible by nheads"
        self.E_head = E_total // nheads
        self.bias = bias

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attn_mask=None,
        is_causal=False,
    ) -> torch.Tensor:
        """
        Forward pass; runs the following process:
            1. Apply input projection
            2. Split heads and prepare for SDPA
            3. Run SDPA
            4. Apply output projection

        Args:
            query (torch.Tensor): query of shape (``N``, ``L_q``, ``E_qk``)
            key (torch.Tensor): key of shape (``N``, ``L_kv``, ``E_qk``)
            value (torch.Tensor): value of shape (``N``, ``L_kv``, ``E_v``)
            attn_mask (torch.Tensor, optional): attention mask of shape (``N``, ``L_q``, ``L_kv``) to pass to SDPA. Default: None
            is_causal (bool, optional): Whether to apply causal mask. Default: False

        Returns:
            attn_output (torch.Tensor): output of shape (N, L_t, E_q)
        """
        # Step 1. Apply input projection
        if self._qkv_same_embed_dim:
            if query is key and key is value:
                result = self.packed_proj(query)
                query, key, value = torch.chunk(result, 3, dim=-1)
            else:
                q_weight, k_weight, v_weight = torch.chunk(
                    self.packed_proj.weight, 3, dim=0
                )
                if self.bias:
                    q_bias, k_bias, v_bias = torch.chunk(
                        self.packed_proj.bias, 3, dim=0
                    )
                else:
                    q_bias, k_bias, v_bias = None, None, None
                query, key, value = (
                    F.linear(query, q_weight, q_bias),
                    F.linear(key, k_weight, k_bias),
                    F.linear(value, v_weight, v_bias),
                )

        else:
            query = self.q_proj(query)
            key = self.k_proj(key)
            value = self.v_proj(value)

        # Step 2. Split heads and prepare for SDPA
        # reshape query, key, value to separate by head
        # (N, L_t, E_total) -> (N, L_t, nheads, E_head) -> (N, nheads, L_t, E_head)
        query = query.unflatten(-1, [self.nheads, self.E_head]).transpose(1, 2)
        # (N, L_s, E_total) -> (N, L_s, nheads, E_head) -> (N, nheads, L_s, E_head)
        key = key.unflatten(-1, [self.nheads, self.E_head]).transpose(1, 2)
        # (N, L_s, E_total) -> (N, L_s, nheads, E_head) -> (N, nheads, L_s, E_head)
        value = value.unflatten(-1, [self.nheads, self.E_head]).transpose(1, 2)

        # Step 3. Run SDPA
        # (N, nheads, L_t, E_head)
        attn_output = F.scaled_dot_product_attention(
            query, key, value, dropout_p=self.dropout, is_causal=is_causal
        )
        # (N, nheads, L_t, E_head) -> (N, L_t, nheads, E_head) -> (N, L_t, E_total)
        attn_output = attn_output.transpose(1, 2).flatten(-2)

        # Step 4. Apply output projection
        # (N, L_t, E_total) -> (N, L_t, E_out)
        attn_output = self.out_proj(attn_output)

        return attn_output
```



[分析transformer模型的参数量、计算量、中间激活、KV cache - 知乎](https://zhuanlan.zhihu.com/p/624740065)