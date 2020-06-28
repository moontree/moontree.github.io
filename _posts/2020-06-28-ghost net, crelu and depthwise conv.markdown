---
layout: post
title:  "Ghost net, crelu, and depthwise convolution"
date:   2020-06-28
categories: deeplearning
author: moontree
---

# GhostNet
GhostNet是一篇CVPR2020的论文，先上论文链接
[《GhostNet: More Features from Cheap Operations》]([https://arxiv.org/pdf/1911.11907.pdf)
和[GitHubd地址](https://github.com/huawei-noah/ghostnet)。

论文的核心思想是，CNN模型中，特征图存在显著的冗余，通过观察特征，可以发现，由若干个特征可以从一个特征
的线性变换得到。

![图1](/static/img/ghost_feature.jpg)

图1对ResNet-50的特征图进行可视化，
并强调了3组特征图内部可以通过线性变化得到（小扳手）。

这样的话，一组特征可以通过一次卷积操作加上一次线性变换得到，从而减少参数数量和计算数量。
那么，对应的ghost模块是什么结构呢？请见下图。

![](/static/img/ghost_module.png)

其实很简单，就是由一次普通的卷积，加上一次深度可分离卷积，然后将两者拼接在一起得到的，具体可以参见github代码。

# CRelu
在看到GhostNet这篇论文的时候，第一反应就是想到了很久之前的一篇论文，[Crelu](https://arxiv.org/pdf/1603.05201.pdf)。似乎是我所知的的，
在特征层面上分析之后，做出改变的第一篇论文。

![](/static/img/celu_histogram.png)

我们来看上图，一个卷积层有 `j=1,…,n` n 个卷积核(filter)。
一个卷积核 $ϕi$
对应的pairing filter定义为 $ϕi=argminϕjcos<ϕi,ϕj>$.
即从所有卷积核中选择一个cos相似度最小的卷积核。

上图的含义是：对所有卷积核寻找其pair filter，并计算cos相似度得到蓝色的统计直方图。
红色的曲线，是假设随机高斯分布生成的卷积核得到的相似度统计。


可以发现，网络的前部，参数的分布有更强的负相关性(类似于正负对立)。随着网络变深，这种负相关性逐步减弱。
而ReLU会将负相位的信息归0，导致了特征和参数的冗余，为了减少冗余，在前几层可以
直接将relu之前的输出取反，和之前的输出拼接在一起，经过relu激活函数，就同时用到了正负输出的信息。
需要注意的是，使用crelu的话， 输出通道数会变成输入的两倍。

# depthwise convolution
最初是Separable Convolution的一部分，Google的[Xception](http://openaccess.thecvf.com/content_cvpr_2017/papers/Chollet_Xception_Deep_Learning_CVPR_2017_paper.pdf)
以及[MobileNet](https://arxiv.org/pdf/1704.04861.pdf)论文中均有描述。
它的核心思想是将一个完整的卷积运算分解为两步进行，
分别为Depthwise Convolution与Pointwise Convolution。

深度可分离卷积，是分布对输入的每个channel进行卷积，得到同样或者n倍的输出，
也是ghostnet第二步的基础操作。

和传统卷积的区别可以通过以下几张图片来进行说明。

## 常规卷积运算
![](/static/img/convolution.jpeg)

假设输入层为一个大小为64×64像素、三通道彩色图片。
经过一个包含4个Filter的卷积层，最终输出4个Feature Map，且尺寸与输入层相同。
整个过程可以用上图来概括。
此时，卷积层共4个Filter，每个Filter包含了3个Kernel，每个Kernel的大小为3×3。
因此卷积层的参数数量可以用如下公式来计算：
```
N_std = 4 × 3 × 3 × 3 = 108
```
## Depthwise Convolution
同样是上述例子，一个大小为64×64像素、三通道彩色图片首先经过第一次卷积运算，
不同之处在于此次的卷积完全是在二维平面内进行，且Filter的数量与上一层的Depth相同。
所以一个三通道的图像经过运算后生成了3个Feature map，如下图所示。

![](/static/img/depthwise_convolution.jpeg)

其中一个Filter只包含一个大小为3×3的Kernel，卷积部分的参数个数计算如下：
```
N_depthwise = 3 × 3 × 3 = 27
```
Depthwise Convolution完成后的Feature map数量与输入层的depth相同，
但是这种运算对输入层的每个channel独立进行卷积运算后就结束了，
没有有效的利用不同map在相同空间位置上的信息。
因此需要增加另外一步操作来将这些map进行组合生成新的Feature map，
即接下来的Pointwise Convolution。

## Pointwise Convolution
Pointwise Convolution的运算与常规卷积运算非常相似，
不同之处在于卷积核的尺寸为 1×1×M，M为上一层的depth。
所以这里的卷积运算会将上一步的map在深度方向上进行加权组合，
生成新的Feature map。有几个Filter就有几个Feature map。
如下图所示。

![](/static/img/pointwise_convolution.jpeg)

由于采用的是1×1卷积的方式，此步中卷积涉及到的参数个数可以计算为：
```
N_pointwise = 1 × 1 × 3 × 4 = 12
```
经过Pointwise Convolution之后，同样输出了4张Feature map，与常规卷积的输出维度相同。

回顾一下，常规卷积的参数个数为：
```
N_std = 4 × 3 × 3 × 3 = 108
```
Separable Convolution的参数由两部分相加得到：
```
N_depthwise = 3 × 3 × 3 = 27
N_pointwise = 1 × 1 × 3 × 4 = 12
N_separable = N_depthwise + N_pointwise = 39
```
相同的输入，同样是得到4张Feature map，
Separable Convolution的参数个数是常规卷积的约1/3。
