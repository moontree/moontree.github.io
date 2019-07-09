---
layout: post
title:  "some functions in tensorflow"
date:   2019-04-17
categories: tensorflow
author: moontree
---

# `tf.meshgrid()`
用于从N个一维向量,返回 N 维坐标数组的列表输出,用于计算 N 维网格上的表达式.
```
a, b = [0, 1, 2], [0, 1, 2]
c = [0, 1, 2]
A, B , C = tf.meshgrid(a, b, c, indexing='ij')
A = tf.expand_dims(A, -1)
B = tf.expand_dims(B, -1)
C = tf.expand_dims(C, -1)

coor = tf.concat((A, B, C), -1)

with tf.Session() as sess:
    print(coor.eval())
```
```
输出
[
[[0, 0, 0], [0, 0, 1], [0, 0, 2]],
[[0, 1, 0], [0, 1, 1], [0, 1, 2]],
[[0, 2, 0], [0, 2, 1], [0, 2, 2]],
[[1, 0, 0], [1, 0, 1], [1, 0, 2]],
[[1, 1, 0], [1, 1, 1], [1, 1, 2]],
[[1, 2, 0], [1, 2, 1], [1, 2, 2]],
[[2, 0, 0], [2, 0, 1], [2, 0, 2]],
[[2, 1, 0], [2, 1, 1], [2, 1, 2]],
[[2, 2, 0], [2, 2, 1], [2, 2, 2]],
```