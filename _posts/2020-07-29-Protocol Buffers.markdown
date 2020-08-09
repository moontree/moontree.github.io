---
layout: post
title:  "Protobuf探索"
date:   2020-07-29
categories: protobuf, c++
author: moontree
---

# Protobuf相关总结

最近重新开始了C++开发，发现公司内部大多数都在用proto来进行数据结构和接口定义，
之前大概了解过一些，但是不够深入。 趁着最近有空，读了一下官方文档，结合实际应用的场景，发现了一些
很实用的应用方式。在这里做个总结。

https://github.com/protocolbuffers/protobuf

## Protobuf是什么
Protobuf实际是一套类似Json或者XML的数据传输格式和规范，
用于不同应用或进程之间进行通信时使用。
通信时所传递的信息是通过Protobuf定义的message数据结构进行打包，
然后编译成二进制的码流再进行传输或者存储。

## Protobuf的优点
相比较而言，Protobuf有如下优点：
- 足够简单
- 序列化后体积很小:消息大小只需要XML的1/10 ~ 1/3
- 解析速度快:解析速度比XML快20 ~ 100倍
- 多语言支持-
- 更好的兼容性,Protobuf设计的一个原则就是要能够很好的支持向下或向上兼容

## 安装及编译
- python
```
pip install protobuf    # 安装protobuf库
sudo apt-get install protobuf-compiler  # 安装protobuf编译器
```
编译为python版本：
``
### 结合grpc,对外提供服务
首先需要安装grpcio和编译工具
```
pip install grpcio
pip install grpcio-tools
```
编译命令如下：
```
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. *.proto
```
python_out指的是proto的python版本输出目录，
grpc_python_out指的是proto的grpc python版本输出目录。

##
