# confusion matrix

## 0. 问题背景

系统梳理一下二分类、多分类的混淆矩阵的概念以及torch实现。

## 1. 什么是混淆矩阵

简单而言，[混淆矩阵](https://machine-learning.paperspace.com/wiki/confusion-matrix)就是一个用来描述一个**分类**模型优劣的基础评价指标，基础指的是许多耳熟能详的指标例如准确率 (Accuracy)，精确率 (Precision), 召回率 (Recall), F1-Score, 交并比 (IOU) 等都是基于混淆矩阵进行计算的。

混淆矩阵的计算是依靠计数，是**离散**的，所以混淆矩阵本身及其衍生指标都是不可导不可微的，是**评估指标** (evaluation matric)，而不是损失函数 (loss function)。

## 2. 二分类和多分类的混淆矩阵

可以参考[多分类混淆矩阵详解与代码实现](https://blog.csdn.net/qq_52466006/article/details/127633149)

需要注意的是：

- 准确率是针对所有类
- 精确率、召回率、F1_score、IOU都是针对单独一类（在二分类中仅仅针对正类），所以多分类的这些计算出来应当是个列表。

## 3. 混淆矩阵的torch实现

- 下面代码实现细节中使用了一个小trick，那就是在计数分类结果的时候，通过乘以类别数 self.num_class，真实标签的值被提升到一个新的范围，从而确保真实标签和预测标签的组合不会重叠（假设类别数量小于 256，这样加法不会超出存储范围），再统计每个组合的出现次数即可完美实现混淆矩阵的计算。从而避免循环。

```python
class Evaluator(object):
    def __init__(self, num_class):
        self.num_class = num_class
        self.confusion_matrix = np.zeros((self.num_class,)*2)

    def OverallAccuracy(self):  
        #  返回所有类的整体像素精度OA
        # acc = (TP + TN) / (TP + TN + FP + TN)  
        OA = np.diag(self.confusion_matrix).sum() / self.confusion_matrix.sum()  
        return OA
    
    def Precision(self):  
        #  返回所有类别的精确率precision  
        precision = np.diag(self.confusion_matrix) / self.confusion_matrix.sum(axis = 0)
        return precision  

    def Recall(self):
        #  返回所有类别的召回率recall
        recall = np.diag(self.confusion_matrix) / self.confusion_matrix.sum(axis = 1)
        return recall
    
    def F1Score(self):
        precision = self.Precision()
        recall = self.Recall()
        f1score = 2 * precision * recall / (precision + recall)
        return f1score

    def IntersectionOverUnion(self):  
        #  返回交并比IoU
        intersection = np.diag(self.confusion_matrix)  
        union = np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) - np.diag(self.confusion_matrix)
        IoU = intersection / union
        return IoU

    def MeanIntersectionOverUnion(self):  
        #  返回平均交并比mIoU(平均指的是所有类别的平均值)
        intersection = np.diag(self.confusion_matrix)  
        union = np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) - np.diag(self.confusion_matrix)
        IoU = intersection / union
        mIoU = np.nanmean(IoU)  
        return mIoU
    
    def Frequency_Weighted_Intersection_over_Union(self):
        #  返回频权交并比FWIoU
        freq = np.sum(self.confusion_matrix, axis=1) / np.sum(self.confusion_matrix)
        iu = np.diag(self.confusion_matrix) / (
                    np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) -
                    np.diag(self.confusion_matrix))

        FWIoU = (freq[freq > 0] * iu[freq > 0]).sum()
        return FWIoU
    
    def _generate_matrix(self, gt_image, pre_image):
        if 'torch' in str(gt_image.dtype):
            gt_image = gt_image.cpu()
            gt_image = gt_image.numpy()
        if 'torch' in str(pre_image.dtype):
            pre_image = pre_image.cpu()
            pre_image = pre_image.numpy()
        gt_image = gt_image.astype('int') 
        pre_image = pre_image.astype('int')
        mask = (gt_image >= 0) & (gt_image < self.num_class)
        # 通过乘以 self.num_class，真实标签的值被提升到一个新的范围，从而确保真实标签和预测标签的组合不会重叠（假设类别数量小于 256，这样加法不会超出存储范围）。
        label = self.num_class * gt_image[mask] + pre_image[mask]
        # 统计每个组合的出现次数
        count = np.bincount(label, minlength=self.num_class**2)
        confusion_matrix = count.reshape(self.num_class, self.num_class)
        return confusion_matrix

    def add_batch(self, gt_image, pre_image):
        assert gt_image.shape == pre_image.shape
        self.confusion_matrix += self._generate_matrix(gt_image, pre_image)

    def reset(self):
        self.confusion_matrix = np.zeros((self.num_class,) * 2)
```

