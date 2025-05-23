# 层归一化LayerNorm

## 0. 问题背景

在深度学习中，尤其是自然语言处理和序列建模任务中，神经网络模型通常包含数十甚至数百层非线性变换。在训练这类深层模型时，梯度消失、梯度爆炸以及内部协变量偏移（internal covariate shift）等问题会严重影响模型的训练效率与稳定性。

为了缓解这些问题，研究者们提出了多种归一化技术。最早流行的是 **Batch Normalization**，它通过对每一层的输入在 mini-batch 维度上进行标准化，加速了图像模型的收敛。但在处理变长序列、在线推理或 batch size 很小的情况下，BatchNorm 的效果会大打折扣，甚至完全不适用。

为了解决这些限制，**Layer Normalization（层归一化）** 被提出。它不依赖 batch 维度，而是对每个样本自身的特征维度进行归一化，因此更适合 Transformer 等自注意力结构中的序列建模任务。

LayerNorm 在 Transformer、BERT、GPT 等模型中已经成为不可或缺的标准组件，它能够有效缓解训练过程中的不稳定性，提高模型泛化能力，是构建现代深度模型的关键模块之一。

