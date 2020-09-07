# --*-- coding: utf-8 --*--
"""
=========================
project -> file: moontree.github.io -> tf_embedding_lookup.py
author: zhangchao
datetime: 2020/9/7 2:16 PM
=========================
"""
import tensorflow as tf
import numpy as np

#  demo1
# per_shard_nums = 10
# # 10 * 1
#
# weights = []
#
# for i in range(100):
#     emb = tf.get_variable(
#         'words-%02d' % i,
#         initializer=tf.constant(
#             # np.reshape(np.arange(i * per_shard_nums, i * per_shard_nums + per_shard_nums), (-1, 1))
#             np.arange(i * per_shard_nums, i * per_shard_nums + per_shard_nums)
#         )
#     )
#     weights.append(emb)
#
# idx = tf.placeholder(tf.int64, shape=[None])
#
# embedding = tf.nn.embedding_lookup(weights, idx, partition_strategy='mod')
# embedding_2 = tf.nn.embedding_lookup(weights, idx, partition_strategy='div')
#
# sess = tf.InteractiveSession()
# sess.run(tf.global_variables_initializer())
# # print(sess.run(weights))
#
# print(sess.run(embedding, feed_dict={idx: [0, 1, 2, 99, 999, 100]}))
# print(sess.run(embedding_2, feed_dict={idx: [0, 1, 2, 99, 999, 100]}))


#  demo2
partitioner = tf.fixed_size_partitioner(100, axis=0)
with tf.variable_scope("embedding", partitioner=partitioner):
    weights = tf.get_variable(
        "weights",
        [1000],
        initializer=np.arange(1000),
        partitioner=partitioner
    )

idx = tf.placeholder(tf.int64, shape=[None])

embedding = tf.nn.embedding_lookup(weights, idx, partition_strategy='mod')
embedding_2 = tf.nn.embedding_lookup(weights, idx, partition_strategy='div')

sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())
print(sess.run(weights))

print(sess.run(embedding, feed_dict={idx: [0, 1, 2, 99, 999, 100]}))
print(sess.run(embedding_2, feed_dict={idx: [0, 1, 2, 99, 999, 100]}))
