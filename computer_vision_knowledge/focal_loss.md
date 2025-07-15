# Focal Loss

## 0. 问题背景

Focal Loss 基本每一个做计算机视觉的都会了解到，其核心思想是：让“难分类的样本”贡献更大的 loss，降低“容易分类的样本”的影响。是很好的应对样本不平衡问题的损失函数。

## 1. Focal Loss的定义

Focal loss 起源于[交叉熵损失函数CE_Loss](./CE_loss.md)

$$
\mathrm{CE}(p, y)=-\sum_{t=1}^C y_t \log \left(p_t\right)
$$

其中， $C$ 是类别数， $p$ 是模型预测的每一类的概率， $y$ 是真实标签(one-hot)，假设第 $t$ 类是对应的类别，所以只有 $y_t = 1$ ，所以公式可以简化为：

$$
\mathrm{CE}(p, y) = -\log \left(p_t\right)
$$

Focal Loss 就是在交叉熵的基础上加了调节系数 $-\alpha_t\left(1-p_t\right)^\gamma$ ：

$$
\mathrm{FL}(p, y)=-\alpha_t\left(1-p_t\right)^\gamma \log \left(p_t\right)
$$

- 其中 $\alpha$ 是权重系数，越大模型越关注某一类，一般取0.25
- $\gamma$ 是聚焦系数（focal strength），越大模型越关注难分样本，一般取2

## 2. $\alpha$ 的理解

模型按照 正类: 负类 = $\alpha$ : $1-\alpha$ 的比例去关注样本，0.25 本质是更关注负样本的，但是这个需要和 $\gamma$ 结合使用。

## 3. $\gamma$ 的理解

模型按照 $\left(1-p_t\right)^\gamma$ 的关注度去动态地关注样本，样本越难分， $p_t$ 越小， $\left(1-p_t\right)^\gamma$ 越大，模型越关注。 $\gamma$ 越大，关注越多，在正负样本失衡的情况下，正样本本身就很难，已经够关注正样本了，所以原论文中 $\alpha$ 取了0.25来稍微抑制一下。

## 4.代码实现

实现一：segmentation-models-pytorch 官方实现

```python

def focal_loss_with_logits(
    output: torch.Tensor,
    target: torch.Tensor,
    gamma: float = 2.0,
    alpha: Optional[float] = 0.25,
    reduction: str = "mean",
    normalized: bool = False,
    reduced_threshold: Optional[float] = None,
    eps: float = 1e-6,
) -> torch.Tensor:
    """Compute binary focal loss between target and output logits.
    See :class:`~pytorch_toolbelt.losses.FocalLoss` for details.

    Args:
        output: Tensor of arbitrary shape (predictions of the model)
        target: Tensor of the same shape as input
        gamma: Focal loss power factor
        alpha: Weight factor to balance positive and negative samples. Alpha must be in [0...1] range,
            high values will give more weight to positive class.
        reduction (string, optional): Specifies the reduction to apply to the output:
            'none' | 'mean' | 'sum' | 'batchwise_mean'. 'none': no reduction will be applied,
            'mean': the sum of the output will be divided by the number of
            elements in the output, 'sum': the output will be summed. Note: :attr:`size_average`
            and :attr:`reduce` are in the process of being deprecated, and in the meantime,
            specifying either of those two args will override :attr:`reduction`.
            'batchwise_mean' computes mean loss per sample in batch. Default: 'mean'
        normalized (bool): Compute normalized focal loss (https://arxiv.org/pdf/1909.07829.pdf).
        reduced_threshold (float, optional): Compute reduced focal loss (https://arxiv.org/abs/1903.01347).

    References:
        https://github.com/open-mmlab/mmdetection/blob/master/mmdet/core/loss/losses.py
    """
    target = target.type(output.type())

    logpt = F.binary_cross_entropy_with_logits(output, target, reduction="none")
    pt = torch.exp(-logpt)

    # compute the loss
    if reduced_threshold is None:
        focal_term = (1.0 - pt).pow(gamma)
    else:
        focal_term = ((1.0 - pt) / reduced_threshold).pow(gamma)
        focal_term[pt < reduced_threshold] = 1

    loss = focal_term * logpt

    if alpha is not None:
        loss *= alpha * target + (1 - alpha) * (1 - target)

    if normalized:
        norm_factor = focal_term.sum().clamp_min(eps)
        loss /= norm_factor

    if reduction == "mean":
        loss = loss.mean()
    if reduction == "sum":
        loss = loss.sum()
    if reduction == "batchwise_mean":
        loss = loss.sum(0)

    return loss

class FocalLoss(_Loss):
    def __init__(
        self,
        mode: str,
        alpha: Optional[float] = None,
        gamma: Optional[float] = 2.0,
        ignore_index: Optional[int] = None,
        reduction: Optional[str] = "mean",
        normalized: bool = False,
        reduced_threshold: Optional[float] = None,
    ):
        """Compute Focal loss

        Args:
            mode: Loss mode 'binary', 'multiclass' or 'multilabel'
            alpha: Prior probability of having positive value in target.
            gamma: Power factor for dampening weight (focal strength).
            ignore_index: If not None, targets may contain values to be ignored.
                Target values equal to ignore_index will be ignored from loss computation.
            normalized: Compute normalized focal loss (https://arxiv.org/pdf/1909.07829.pdf).
            reduced_threshold: Switch to reduced focal loss. Note, when using this mode you
                should use `reduction="sum"`.

        Shape
             - **y_pred** - torch.Tensor of shape (N, C, H, W)
             - **y_true** - torch.Tensor of shape (N, H, W) or (N, C, H, W)

        Reference
            https://github.com/BloodAxe/pytorch-toolbelt

        """
        assert mode in {BINARY_MODE, MULTILABEL_MODE, MULTICLASS_MODE}
        super().__init__()

        self.mode = mode
        self.ignore_index = ignore_index
        self.focal_loss_fn = partial(
            focal_loss_with_logits,
            alpha=alpha,
            gamma=gamma,
            reduced_threshold=reduced_threshold,
            reduction=reduction,
            normalized=normalized,
        )

    def forward(self, y_pred: torch.Tensor, y_true: torch.Tensor) -> torch.Tensor:
        if self.mode in {BINARY_MODE, MULTILABEL_MODE}:
            y_true = y_true.view(-1)
            y_pred = y_pred.view(-1)

            if self.ignore_index is not None:
                # Filter predictions with ignore label from loss computation
                not_ignored = y_true != self.ignore_index
                y_pred = y_pred[not_ignored]
                y_true = y_true[not_ignored]

            loss = self.focal_loss_fn(y_pred, y_true)

        elif self.mode == MULTICLASS_MODE:
            num_classes = y_pred.size(1)
            loss = 0

            # Filter anchors with -1 label from loss computation
            if self.ignore_index is not None:
                not_ignored = y_true != self.ignore_index

            for cls in range(num_classes):
                cls_y_true = (y_true == cls).long()
                cls_y_pred = y_pred[:, cls, ...]

                if self.ignore_index is not None:
                    cls_y_true = cls_y_true[not_ignored]
                    cls_y_pred = cls_y_pred[not_ignored]

                loss += self.focal_loss_fn(cls_y_pred, cls_y_true)  # 多个二分类的loss相加

        return loss
    
    
```

- 可以看到在实现多分类的Focal Loss的过程中，是转换为计算多个二分类实现的
- 优点：支持二分类、多分类、多标签；支持不同的聚合方式；支持reduced focal loss
- 缺点：多分类无法支持 $\alpha$ 为一个list来为不同的类别赋予不同的权重系数

实现二：

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class FocalLoss(nn.Module):
    def __init__(self, gamma: float, alpha: Optional[torch.Tensor] = None):
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.alpha = alpha  # [C,]

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return focal_loss(input, target, self.gamma, self.alpha)

def focal_loss(pred_logit: torch.Tensor,
               label: torch.Tensor,
               gamma: float,
               alpha: Optional[torch.Tensor] = None) -> torch.Tensor:
    # pred_logit [B, C]  or  [B, C, X1, X2, ...]
    # label [B, ]  or  [B, X1, X2, ...]
    B, C = pred_logit.shape[:2]  # batch size and number of categories
    if pred_logit.dim() > 2:
        # e.g. pred_logit.shape is [B, C, X1, X2]   
        pred_logit = pred_logit.reshape(B, C, -1)  # [B, C, X1, X2] => [B, C, X1*X2]
        pred_logit = pred_logit.transpose(1, 2)    # [B, C, X1*X2] => [B, X1*X2, C]
        pred_logit = pred_logit.reshape(-1, C)   # [B, X1*X2, C] => [B*X1*X2, C]   set N = B*X1*X2
    label = label.reshape(-1)  # [N, ]

    log_p = torch.log_softmax(pred_logit, dim=-1)  # [N, C]
    log_p = log_p.gather(1, label[:, None]).squeeze()  # [N,]
    p = torch.exp(log_p)  # [N,]
    
    if alpha is None:
        alpha = torch.ones((C,), dtype=torch.float, device=pred_logit.device)
    alpha = alpha.gather(0, label)  # [N,]
    
    loss = -1 * alpha * torch.pow(1 - p, gamma) * log_p
    return loss.sum() / alpha.sum()


if __name__ == "__main__":
    import numpy as np
    
    B, C, X1, X2 = 32, 4, 100, 200
    pred_logit = np.random.randn(B, C, X1, X2)
    pred_logit1 = torch.tensor(pred_logit, dtype=torch.float, requires_grad=True)
    pred_logit2 = torch.tensor(pred_logit, dtype=torch.float, requires_grad=True)
    
    label = np.random.randint(0, C, size=(B, X1, X2))
    label = torch.tensor(label, dtype=torch.long)
    
    alpha = np.abs(np.random.randn(C))
    alpha = torch.tensor(alpha, dtype=torch.float)
    
    loss1 = FocalLoss(gamma=0.0, alpha=alpha)(pred_logit1, label)
    loss1.backward()
    
    loss2 = F.cross_entropy(pred_logit2, label, weight=alpha)
    loss2.backward()
    
    print(loss1)
    print(loss2)
    print(pred_logit1.grad[1, 2, 3, 4])
    print(pred_logit2.grad[1, 2, 3, 4])
    
    
```

