---
layout: post
title:  "bilateral filter 到 HDRnet"
date:   2020-10-19
categories: tensorflow, cv, style transfer
author: moontree
---

上次介绍过了Style Transfer的一系列文章，但是可以发现，哪怕是最后一篇ADIN，也已经是2017年了。
那么，近几年大家都在做什么呢？

搜索关键词的时候，发现大家都在做`Photorealistic Style Transfer`，对目标图片的真实感有了更高的要求。

正如Style Transfer的基础是[Image Style Transfer Using Convolutional Neural Networks](https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Gatys_Image_Style_Transfer_CVPR_2016_paper.pdf)
一样， Photorealistic Style Transfer也有其理论基础，即 Bilateral Filter （双边滤波器）。

## Bilateral Filter

在cv领域，对图像进行滤波是常见的操作，通用公式如下：
$$
I^o_p = \frac{\sum_qI(p)w(p, q)}{\sum_qw(p, q)}  \tag{1}
$$

这里$I(p)$代表图像，p,q是图像上的坐标，$w(p,q)$代表与位置相关的权重。
大多数滤波器的区别就在于权重的选择。

以高斯滤波来说，
$$
w(p,q) = G_{\sigma}(|| p - q ||) = \frac{1}{2\pi \sigma^2}exp(-\frac{|| p - q || ^ 2}{2\sigma^2})  \tag{2}
$$

只考虑了p,q的距离，距离越远，权重越低；这样可以用来做平滑，但是会导致边缘被摸糊掉。
```
# for pixel[x][y]
new_pixel[x][y] = 0
k = 0
for i in range(-r, r + 1):
    for j in range(-r, r + 1):
        new_pixel[x][y] += pixel[i + x][j + y] * c[i][j]
        k += c[i][j]
new_pixel[x][y] /= k
```

而双边滤波则同时考虑了p,q两点的距离和像素值相似程度：
距离越近、相似程度越高，权重越大。
$$
w(p,q) = G_{\sigma_s}(||p-q|)G_{\sigma_r}(||I(p) - I(q)||)  \tag{3}
$$

```
# for pixel[x][y]
new_pixel[x][y] = 0
k = 0
for i in range(-r, r + 1):
    for j in range(-r, r + 1):
        w = c[i][j] * s(pixel[x][y], pixel[i + x][j + y])
        new_pixel[x][y] += pixel[i + x][j + y] * w
        k += w
new_pixel[x][y] /= k
```

这样的话，同时考虑空域信息和灰度相似性，
达到保边去噪的目的。具有简单、非迭代、局部的特点。
但是由于保存了过多的高频信息，对于彩色图像里的高频噪声，
双边滤波器不能够干净的滤掉，只能够对于低频信息进行较好的滤波。
![bilateral filter](/static/img/bilateral_filter.jpg)

然而，在保留边缘信息的时候，双边滤波的计算量也增加了许多。

有没有办法进行加速呢？

考虑到高斯滤波的过程，其实和2D卷积是一样的；很显然，双边滤波的计算过程和3D卷积的计算过程也是一样的，
是不是可以借鉴一下呢？

先计算出p(x,y)和q的值，offset作为第三位，像素差作为对应的值，应该也是可以的。但是仔细想想，感觉哪里不太对，
相当于卷积核在发生变化？

## [A Fast Approximation of the Bilateral Filter using a Signal Processing Approach](https://link.zhihu.com/?target=https%3A//dspace.mit.edu/bitstream/handle/1721.1/34876/MIT-CSAIL-TR-2006-073.pdf%3Fsequence%3D1)

