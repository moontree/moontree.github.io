---
layout: post
title:  "Tone Mapping（色调映射）"
date:   2020-08-30
categories: cv, 图像风格
author: moontree
---

读论文的时候，看到了"Tone Mapping"这个超出我知识范围的词语，就很好奇，这究竟是个什么东西呢？
就把了解到的信息做个记录吧，方便以后查阅。



## HDR与LDR

### HDR(High Dynamic Range)
什么是HDR，首先我们来理解DR——Dynamic Range（动态范围）：Dynamic Range是一种用数学方式来描述某个给定场景的亮度层次范围的技术术语。
指图像中所包含的从“最亮”至“最暗”的比值，也就是图像从“最亮”到“最暗”之间灰度划分的等级数；
动态范围越大，所能表示的层次越丰富，所包含的色彩空间也越广。

最通常的解释有两种：
- 一种是摄影界通常所说的D值（以对数值表示的场景最高亮度和最低亮度比的相对数值），通常由0-4之间的很精确的数字来表示。
D值的计算公式为：Dynamic Range=log10(Max Intensity / Min Intensity)。
公式中intensity是指光照强度，我们对最大亮度除以最低亮度的结果取对数，得到的结果就是动态范围的相对数值——摄影界所说的D值。
各种景物、底片和照片都有其各自特定的D值范围。
- 另一种是计算机图形学中通常使用的直接以场景最高亮度和最低亮度的亮度比表述的方法，如255:1。
在数字图像领域一般都采用这第二种比值的表述方式来评述场景的动态范围。

亮度的单位以每平方米的烛光来表示（cd/m2）。
太阳自身的亮度大约为1,000,000,000 cd/m2。
阳光照射下的景物的亮度可达100,000 cd/m2，而星光的亮度大约在0.001 cd/m2以下，二者亮度比达亿倍以上。
现实中人类的眼睛所能看到亮度比的范围是$10^5$左右，相对于255:1来说，我们称之为高动态范围，即HDR。

### LDR(Low Dynamic Range Image)
什么是LDR？它所采用的色彩模型是目前通用的图像描述模型——RGB模型。
每种色彩都可以用三原色（红、绿、蓝）加上适当的亮度来表示，三原色的亮度梯度各为256级。
选定每色256级是在电脑硬件性能、照片级真彩图片需要和电脑2进制方案综合考虑后的结果。
这就是目前我们非常熟习的观看、编辑、交换和处理数字图像的软硬件环境。
这种8比特位元RGB低动态范围图像描述模型是将场景最高亮度和最低亮度的亮度比限定为255比1，计算得出的动态范围D值即为2.4。

## Tone Mapping
Tone mapping自古以来一直都有，不是计算机图形学的专利。
早期因为颜料的对比度有限，达芬奇等的高手会把需要表达的内容用很有限的颜色画出来，即便色彩不真实。
而刚发明电影的时候，胶片能表达的亮度范围有限，
所以摄影师会把高亮区域和阴影区域向中等亮度方向压缩，发展出了S曲线的映射关系。
这些都是tone mapping。

下面，我们来看下相关算法的发展,

### 经验派-[Reinhard tone mapping](http://www.cmap.polytechnique.fr/~peyre/cours/x2005signal/hdr_photographic.pdf)

Reinhard tone mapping非常简单，用代码描述就三行。

```
float3 ReinhardToneMapping(float3 color, float adapted_lum) {
    const float MIDDLE_GREY = 1;
    color *= MIDDLE_GREY / adapted_lum;
    return color / (1.0f + color);
}
```

其中color是线性的HDR颜色，adapted_lum是根据整个画面统计出来的亮度。
MIDDLE_GREY表示把什么值定义成灰。这个值就是纯粹的magic number了，根据需要调整。
Reinhard的曲线是这样的，可以看出总体形状是个S型。

![](/static/img/reinhard_curve.png)

这种tone mapping的方法更多地来自于经验，没什么原理在后面。
所以就姑且称它为经验派吧。它的优点是简单直接，把亮的变暗，暗的变量。
这样暗处和亮处细节就都出来了。但缺点也很明显，就是灰暗。
个个颜色都朝着灰色的方向被压缩了，画面像蒙了一层纱。

![](/static/img/reinhard_result.jpg)

### 粗暴派
到了2007年，孤岛危机（Crysis）的CryEngine 2，为了克服Reinhard灰暗的缺点，
开始用了另一个tone mapping的方法。
前面提到了tone mapping就是个S曲线，那么既然你要S曲线，
我就搞出一个S曲线。这个方法更简单，只要一行，而且没有magic number。
用一个exp来模拟S曲线。

```
float3 CEToneMapping(float3 color, float adapted_lum)
{
    return 1 - exp(-adapted_lum * color);
}
```
CE的曲线中间的区域更偏向于小的方向，这部分曲线也更陡。

![](/static/img/ce_curve.png)

这个方法得到的结果比Reinhard有更大的对比度，颜色更鲜艳一些，虽然还是有点灰。

![](/static/img/ce_result.jpg)

CE的方法在于快速，并且视觉效果比Reinhard。但是这个方法纯粹就是凑一个函数，没人知道应该如何改进。属于粗暴地合成。

### 拟合派-Filmic tone mapping]

这个方法的本质是把原图和让艺术家用专业照相软件模拟胶片的感觉，
人肉tone mapping后的结果去做曲线拟合，得到一个高次曲线的表达式。
这样的表达式应用到渲染结果后，就能在很大程度上自动接近人工调整的结果。

最后出来的曲线是这样的。总的来说也是S型，但增长的区域很长。

![](/static/img/filmic_curve.png)

从结果看，对比度更大，而且完全消除了灰蒙的感觉。

![](/static/img/filmic_result.jpg)

而代码就有点复杂了：

```
float3 F(float3 x)
{
	const float A = 0.22f;
	const float B = 0.30f;
	const float C = 0.10f;
	const float D = 0.20f;
	const float E = 0.01f;
	const float F = 0.30f;

	return ((x * (A * x + C * B) + D * E) / (x * (A * x + B) + D * F)) - E / F;
}

float3 Uncharted2ToneMapping(float3 color, float adapted_lum)
{
	const float WHITE = 11.2f;
	return F(1.6f * adapted_lum * color) / F(WHITE);
}
```
那些ABCDEF都是多项式的系数，而WHITE是个magic number，表示白色的位置。
这个方法开启了tone mapping的新路径，让人们知道了曲线拟合的好处。
并且，其他颜色空间的变换，比如gamma矫正，也可以一起合并到这个曲线里来，一次搞定，不会增加额外开销。
缺点就是运算量有点大，两个多项式的计算，并且相除。

因为Filmic tone mapping的优异表现，大部分游戏都切换到了这个方法。
包括CE自己，也在某个时候完成了切换。

### 你们都是渣渣派-[Academy Color Encoding System（ACES](https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/)

在大家以为Filmic tone mapping会统治很长时间的时候，江湖中来了一位异域高手。
他认为，你们这帮搞游戏/实时图形的，都是渣渣。让我们电影业来教你们什么叫tone mapping。
这位高手叫美国电影艺术与科学学会，就是颁布奥斯卡奖的那个机构。
不要以为他们只是个评奖的单位，美国电影艺术与科学学会的第一宗旨就是提高电影艺术与科学的质量。

他们发明的东西叫Academy Color Encoding System（ACES），是一套颜色编码系统，或者说是一个新的颜色空间。
它是一个通用的数据交换格式，一方面可以不同的输入设备转成ACES，另一方面可以把ACES在不同的显示设备上正确显示。
不管你是LDR，还是HDR，都可以在ACES里表达出来。这就直接解决了VDR的问题，不同设备间都可以互通数据。

然而对于实时渲染来说，没必要用全套ACES。
因为第一，没有什么“输入设备”。渲染出来的HDR图像就是个线性的数据，所以直接就在ACES空间中。
而输出的时候需要一次tone mapping，转到LDR或另一个HDR。
也就是说，我们只要ACES里的非常小的一条路径，而不是纷繁复杂的整套体系。

那么这条路径有多小呢？只要几行，系数来自于Krzysztof Narkowicz的博客文章。

```
float3 ACESToneMapping(float3 color, float adapted_lum)
{
	const float A = 2.51f;
	const float B = 0.03f;
	const float C = 2.43f;
	const float D = 0.59f;
	const float E = 0.14f;

	color *= adapted_lum;
	return (color * (A * color + B)) / (color * (C * color + D) + E);
}
```

很像Uncharted 2的做法，都是多项式拟合。但是式子比Uncharted的简单，并不需要算两个多项式并相除，只要算一个，一次搞定。它的曲线是这样的。

![](/static/img/aces_curve.png)

S感很浓，并且比Uncharted的更向小的方向移，即便很小的数值和接近1的数值也有梯度。这样能很好地保留暗处和亮处的细节。至于视觉效果如何呢？看看这个。

![](/static/img/aces_result.jpg)

可以看出来，比之前的任何一个都要鲜艳，并且没有因此丢掉细节！当之无愧成为目前最好的tone mapping算法。
更好的地方是，按照前面说的，ACES为的是解决所有设备之间的颜色空间转换问题。
所以这个tone mapper不但可以用于HDR到LDR的转换，还可以用于从一个HDR转到另一个HDR。
也就是从根本上解决了VDR的问题。这个函数的输出是线性空间的，所以要接到LDR的设备，只要做一次sRGB校正。
要接到HDR10的设备，只要做一次Rec 2020颜色矩阵乘法。Tone mapping部分是通用的，这也是比之前几个算法都好的地方。

目前一些新的游戏，比如Rise of the Tomb Raider、UE 4.8，也都切换到ACES的tone mapping曲线。

## Gamma Correction
早期的 CRT 显示器存在非线性输出的问题,简单来说,你给 CRT 显示器输入(input)一个 0.5(输入范围为[0,1]),
CRT 显示器的输出(output)并不是 0.5,而是约等于 0.218,输入与输出间存在一个指数大概为 2.2 的幂次关系:

![](https://pic1.zhimg.com/v2-8d410eeea31b29f5b522e7629e471a20_b.jpg)

其中 2.2 这个指数即为伽马(gamma)值,而显示器的这种非线性输出过程则称为伽马展开(display gamma).
为了能够得到正确的输出,我们必须对输入进行补偿,方法就是对输入进行一次指数为 $1 / 2.2$ 的幂次运算,
这个补偿的过程便是伽马编码(encoding gamma)我们也称gamma correction :

$input -> input^{\frac{1}{2.2})$


所以为了让显示器正确输出 0.5, 我们需要对 0.5 进行伽马校正,实际给显示器的输入约为 0.73。

看到这里你可能会有个疑问：
既然伽马校正起源于早期 CRT 显示器的非线性输出问题,
而我们现在基本已经淘汰掉这些显示器,并且当今的显示器已经可以做到线性输出了(输入0.5,输出也是0.5),
那么我们是不是可以直接废弃伽马校正了呢?答案可能有些出人意料 :
我们仍然需要进行伽马校正!原因有些巧合 : 伽马校正除了可以解决早期 CRT 显示器的非线性输出问题,
同时还可以帮助我们"改善"输出的图像质量，下图是自然界中的亮度以及对应的人所感受的亮度值 :

![](https://picb.zhimg.com/v2-5da4673b8149b499df7202f54317e2d3_b.jpg)

由上图可以看出，人眼对于较暗(接近0)的亮度值比较敏感,对于较亮(接近1)的亮度值则不太敏感，
你可以理解为人眼更能辨别较暗的亮度值发生的变化，因此颜色在存储时，我们应该更多的保存较暗部分的颜色值。
对于自然界中大约0.218的亮度值，人感受亮度值约为0.5，因此我们有了下面的Gamma Correction和CRT gamma曲线。

![](/static/img/crt_gamma.png)

假设我们现在使用一个字节(能够表达整数范围[0,255])来存储亮度值,并且我们要存储 0.240 和 0.243 这两个亮度值,如果不进行伽马校正,则有:

value1=0.240∗255=61.2⟶取整为61
value2=0.243∗255=61.965⟶取整为61

可以看到 0.240 和 0.243 的存储数值都是 61,所以这两个输入的实际显示效果其实是一样的(细节差异丢失了).
但如果我们进行一次伽马校正,则有:
0.240 和 0.243 的存储数值变为了 133 和 134,
所以这两个输入的实际显示效果便区分开了(细节差异保留了).


实际上,伽马校正增大了较暗数值的表示精度,而减小了较亮数值的表示精度,
人眼又恰好对较暗数值比较敏感,对较亮数值不太敏感,于是从视觉角度讲,输出的图像质量就被伽马校正"改善"了.
基于这个原因,我们仍然需要进行伽马校正,而既然我们进行了伽马校正,
当今的显示器也便保留了非线性输出(伽马展开)的功能。

## 总结
总的来说，Tone Mapping和Gamma Correction二者都是为了更好的在LDR设备上显示图片，
将图片的颜色值从一个范围分布变换到另一个范围分布。
而不同的是，Tone Mapping是根据相应的算法将颜色值从一个大的范围映射到了较小的范围，
而Gamma Correction则是从[0,1]映射到[0,1],
映射范围并没有改变，只是改变了不同亮度值颜色的分布情况。


## References
- [Gamma校正算法原理及实现](https://www.cnblogs.com/Vince-Wu/p/12689602.html)
- [Tone Mapping 与 Gamma Correction](https://zhuanlan.zhihu.com/p/79203830)
- [Tone mapping进化论](https://zhuanlan.zhihu.com/p/21983679)
