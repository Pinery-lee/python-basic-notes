# loss2nan

## 1.问题背景

如题，最近在坐语义分割项目的时候，遇到了 loss 在训练途中突然变为 nan 的情况，这个问题我遇到过两次，如下所示：

```js
2025-07-08 15:53:56,545 - Epoch: 31/99, lr: 0.000083, train_loss: 0.1574, valid_loss: 0.1620
2025-07-08 15:53:56,546 - mAP: 0.8595, mAR: 0.9088, mIOU: 0.7913
2025-07-08 15:53:59,052 - ----------
2025-07-08 15:54:39,765 - Epoch: 32/99, lr: 0.000081, train_loss: 0.1701, valid_loss: 0.2029
2025-07-08 15:54:39,766 - mAP: 0.8441, mAR: 0.8672, mIOU: 0.7475
2025-07-08 15:54:39,766 - ----------
2025-07-08 15:55:20,281 - Epoch: 33/99, lr: 0.000080, train_loss: 0.1758, valid_loss: 0.2343
2025-07-08 15:55:20,282 - mAP: 0.8997, mAR: 0.7719, mIOU: 0.7108
2025-07-08 15:55:20,282 - ----------
2025-07-08 15:56:11,862 - Epoch: 34/99, lr: 0.000079, train_loss: nan, valid_loss: nan
2025-07-08 15:56:11,862 - mAP: nan, mAR: 0.0000, mIOU: 0.0000
2025-07-08 15:56:11,862 - ----------
2025-07-08 15:56:49,467 - Epoch: 35/99, lr: 0.000077, train_loss: nan, valid_loss: nan
2025-07-08 15:56:49,467 - mAP: nan, mAR: 0.0000, mIOU: 0.0000
2025-07-08 15:56:49,468 - ----------
2025-07-08 15:57:36,634 - Epoch: 36/99, lr: 0.000076, train_loss: nan, valid_loss: nan
2025-07-08 15:57:36,634 - mAP: nan, mAR: 0.0000, mIOU: 0.0000
```

## 2.问题反思

- nan 意思是 not a number, 因为使用了非法的数学运算而产生
- 常见非法运算：

````python
import torch
print("\n======= NaN 示例汇总 =======")
# 设置警告显示为错误（可选）
torch.set_printoptions(precision=10)
x = torch.tensor([0.0])
y = -torch.log(x)
print("1. -log(0):", y.item())
x = torch.tensor([-1.0])
y = torch.log(x)
print("2. log(-1):", y.item())
x = torch.tensor([-3.0])
y = torch.sqrt(x)
print("3. sqrt(-3):", y.item())
x = torch.tensor([0.0])
y = x / x
print("4. 0 / 0:", y.item())
x = torch.tensor([float('inf')])
y = x - x
print("5. inf - inf:", y.item())
x = torch.tensor([float('inf')])
y = x * 0
print("6. inf * 0:", y.item())
````

```
======= NaN 示例汇总 =======
1. -log(0): inf
2. log(-1): nan
3. sqrt(-3): nan
4. 0 / 0: nan
5. inf - inf: nan
6. inf * 0: nan
```

- `loss = inf` 本身不会立即中断训练，但：
  - `loss.backward()` 之后，会产生 **梯度为 `inf` 或 `nan`**；
  - 下一步优化器更新 → 参数中也变成 `inf`；
  - 接着 forward 再次变 `inf` 或 `nan`；
  - **最终模型彻底“中毒”**。

## 3.问题解决

第一次遇到是因为我换成了Transformer架构的模型，但是学习率是基于cnn架构模型的较大学习率，我通过适当的降低学习率，除以5~10, 解决了这个问题。

第二次遇到是因为样本标签中有很多全零标签，我将全零标签删除也解决了问题。

第三次遇到了，本来以为已经很小了学习率，还是出现了nan值，我觉得看学习率大不大主要看训练loss的走势

- 如果loss刚开始剧烈下降，同时出现明显震荡，则学习率太大

- 如果loss下降非常慢，则学习率太小

可以在后向传播之后使用梯度裁剪，使得即使比较大的学习率也能够正常训练：

```
loss.backward()
# 如果梯度总范数大于1，则对梯度进行缩放归一化
torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
```