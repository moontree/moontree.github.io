---
layout: post
title:  "导向滤波"
date:   2020-09-09
categories: cv edge-perserving-filter
author: moontree
---

在[bilateral filter 到 HDRnet](https://moontree.github.io/2020/10/19/%E4%BB%8Ebilateral-filter-%E5%88%B0-HDRnet/)这篇文章里，
我们提到了双边滤波可以较好的保持图像的边缘，但是它也有着自己的问题：
- 如果一个像素周围的相似像素较少，会出现梯度反转现象
- 暴力的双边滤波需要$O(Nr^2)$的时间

而导向滤波（guided filter),则可以在保持梯度的同时也有着极大的速度优势，计算时间是线性的O(N)

导向滤波（Guided Filtering）和双边滤波（BF）、最小二乘滤波（WLS）是三大边缘保持（Edge-perserving）滤波器。
当然，引导滤波的功能不仅仅是边缘保持，只有当引导图是原图的时候，它就成了一个边缘保持滤波器。

## 原理
导向滤波的原理图如下所示：

![](/static/img/guided_filter.jpg)

对于输入图像p，通过引导图像I，经过滤波后得到输入图像q，导向滤波是这样计算的：

$$
q_i = a_kI_i + b_k, \forall  i \in w_k \\
q_i = p_i - n_i
$$

导向滤波的一个重要假设是输出图像q和引导图像I在滤波窗口$w_k$上存在局部线性关系。
这样的话，在一个局部区域里，如果引导图像I有一个边缘，输出图像q也保持边缘不变，
因为对于相邻的像素点而言，存在$\bigtriangledown q=\alpha \bigtriangledown I$。
因此，只要求到了系数a,b，也就得到了输出。

同时，我们认为，输入图像p是由输出图像q加上我们不希望的噪声或纹理n得到，因此有p=q+n。

接下来，就是解出这样的系数，使得p、q的差别尽可能小。对于每一个滤波窗口，该算法在最小二乘意义
上的最优化，可以表示为：

$$
argmin \sum_{i \in w_k}(q_i - p_i)^2 \\
argmin \sum_{i \in w_k}(a_kI_i + b_k - p_i)^2
$$

最后，引入一个正则化参数$\epsilon$,防止$a_k$过大，于是有：

$$
E(a_k,b_k) = \sum_{i \in w_k}((a_kI_i + b_k - p_i)^2 + \epsilon a_k^2)
$$

对上述方程进行求解，有:

$$
\frac{\delta E}{a_k} = \sum_{i \in w_k} (2(a_kI_i + b_k - p_i)I_i + 2 \epsilon a_k) = 0 \\
\frac{\delta E}{b_k} = \sum_{i \in w_k}(2(a_kI_i + b_k - p_i)) = 0 \\
a_k = \frac{\sum_{i \in w_k}p_iI_i - b_k \sum_{i \in w_k}I_i}{\sum_{i \in w_k}(I_i^2 + \epsilon)} \\
b_k = \frac{1}{|w|}(\sum_{i \in w_k}p_i - a_k \sum_{i \in w_k}I_i)
$$

将$b_k$带入$a_k$，整理可得：

$$
a_k=\frac{\frac{1}{|w|}\sum_{i \in w_k}I_ip_i - \mu_k \overline{p}_k}{\sigma_k^2 + \epsilon} \\
b_k = \overline{p}_k - a_k \mu_k
$$

在这里，$\mu_k$和$\sigma_k^2$分别表示引导图像I在窗口$w_k$中的平均值和方差，
|w|表示窗口$w_k$内像素点的个数，
$$
\overline{p}_k = \frac{1}{|w|}\sum_{i \in w_k}p_i $$ 表示输入图像在窗口中的平均值。

接下来，将上述线性模型应用到整个图像的滤波窗口即可。但是，每个像素点会被包含到多个窗口里：
如果用3*3的窗口滤波，除了边缘位置，每个点都会抱包含在9个窗口里；每个窗口都会有一个$q_i$值，
对所有的值进行平均，得到最终结果：

$$
q_i=\frac{1}{|w|}\sum_{k:i \in w_k}(a_kI_i + b_k)
=\overline{a}_iI_i + \overline{b}_i
$$

这样，就建立里每个像素点从I到q的映射。

## 边缘保持
对于该算法，输入和引导图像是同一副图像也就是I=p的时候,该算法成为一个边缘保持滤波器，方程的接表示为：

$$
a_k = \frac{\sigma_k^2}{\sigma_k^2 + \epsilon} \\
b_k = (1 - a_k)\overline{p}_k
$$

在这种情况下，$\epsilon$相当于界定平滑区域和便与其按区域的阈值。考虑如下两种情况：
- Case 1：平坦区域。如果在某个滤波窗口内，该区域是相对平滑的，方差$\sigma_k^2$将远远小于$\epsilon$。
从而$a_k \approx 0,b_k \approx \overline{p}_k$。相当于对该区域作均值滤波。

![](/static/img/guided_filter_smooth.png)

- Case 2：高方差区域。相反，如果该区域是边缘区域，方差很大,
方差$\sigma_k^2$将远远大于$\epsilon$。
从而$a_k \approx 1,b_k \approx 0$。相当于在区域保持原有梯度。

![](/static/img/guided_filter_edge_preserve.png)

## 其他应用
羽化、去雾等，请见[ppt](http://kaiminghe.com/eccv10/eccv10ppt.pdf)

## 代码
[链接](https://github.com/moontree/moontree.github.io/blob/master/examples/guided_filter.py)。


## 参考
- https://blog.csdn.net/weixin_43194305/article/details/88959183
- https://zhuanlan.zhihu.com/p/161666126
- http://kaiminghe.com/eccv10/
- http://kaiminghe.com/eccv10/eccv10ppt.pdf
- http://kaiminghe.com/publications/eccv10guidedfilter.pdf
- https://zhuanlan.zhihu.com/p/36813673