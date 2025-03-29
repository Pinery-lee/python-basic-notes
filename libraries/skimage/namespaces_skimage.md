# namespaces_skimage

scikit-image（`skimage`）本身并不包含大量独立的数据结构，其核心设计理念是**基于 NumPy 数组**进行图像处理。

它的子命名空间非常的规整

## skimage

`skimage.__version__`

## skimage.color

颜色空间转换

## skimage.data

内置的许多示例图片

## skimage.draw

在图像上绘制几何形状和文本

## skimage.exposure

图像曝光调整，例如直方图均衡化，伽马校正等

## skimage.feature

特征检测与提取，例如纹理，角度等

## skimage.filters

图像滤波，例如锐化、边缘检测、阈值等

## skimage.future

实验性API

## skimage.graph

基于图的操作，核心数据结构式RAG: 图像的区域邻接图（Region Adjacency Graph, RAG），子类`networkx.graph`

## skimage.io

读取和保存图像和视频

## skimage.measure

图像特性的测量，例如区域特征，轮廓

## skimage.metrics

图像之间的指标，例如距离，相似度，MSE等

## skiamge.morphology

形态学操作

## skimage.registration

用于**图像配准（Image Registration）**的模块，主要目的是将不同时间、视角或传感器捕获的图像进行对齐，使它们在空间上匹配

## skimage.restoration

恢复算法，例如反卷积算法，去噪等

## skimage.segementation

图像分割

## skimage.transform

图像的几何及其他变换

## skiamge.util

通用工具













