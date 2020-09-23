---
layout: post
title:  "自监督学习"
date:   2020-09-09
categories: cv, self-supervised learning
author: moontree
---

图像方面的自监督学习：
生成式、判别式。
## 判别式
关键在于如何构建正样本和负样本。
负样本的数量。
### CPC
### ImagePatch
### SimCLR

### MOCO

### BYOL

## 生成式


## 参考文献
- https://www.zhihu.com/question/402452508/answer/1293771636
- [How Useful is Self-Supervised Pretraining for Visual Tasks](https://arxiv.org/pdf/2003.14323.pdf)定义了 Utility 来衡量 SSL 方法的效率，测试了众多 SSL 方法在各种任务下不同的有效性 。
- [Rethinking Image Mixture for Unsupervised Visual Representation Learning](https://arxiv.org/pdf/2003.05438.pdf) 对比学习里的 Mixup
- [Big Self-Supervised Models are Strong Semi-Supervised Learners](https://arxiv.org/pdf/2006.10029.pdf)SimCLR作者的新作，大力出奇迹。
- [Bootstrap Your Own Latent A New Approach to Self-Supervised Learning]()不需要制造负样本，model 之间互相迭代 teaching 就可以得到很好的 performance。
- [What Makes for Good Views for Contrastive Learning](https://arxiv.org/pdf/2005.10243.pdf)
- https://www.zhihu.com/question/402452508/answer/1294166177