# --*-- coding: utf-8 --*--
"""
=========================
project -> file: moontree.github.io -> guided_filter.py
author: zhangchao
datetime: 2020/9/10 3:46 PM
=========================
"""
import numpy as np
from scipy import signal
import cv2


def helper(I, r):
    """

    :param I: Image
    :param r: local window radis
    :return: same size as I
    """
    kernel = np.ones([r * 2 + 1, r * 2 + 1])

    return signal.convolve2d(I, kernel, mode='same')


def guided_filter(I, p, r, eps):
    h, w = np.shape(I)
    N = helper(np.ones_like(I), 1)
    mean_I = helper(I, r) / N
    mean_p = helper(p, r) / N
    mean_Ip = helper(I * p, r) / N
    conv_Ip = mean_Ip - mean_I * mean_p

    mean_II = helper(I * I, r) / N
    var_I = mean_II - mean_I * mean_I

    a = conv_Ip / (var_I + eps)
    b = mean_p - a * mean_I

    mean_a = helper(a, r) / N
    mean_b = helper(b, r) / N

    q = mean_a * I + mean_b
    return q


if __name__ == "__main__":
    img = cv2.imread("static/img/ce_result.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img / 255.
    cv2.imshow('a', img)

    k = np.ones([5, 5])
    print(helper(k, 1))
    print(np.max(img))
    img2 = guided_filter(img, img, 1, 1e-5)
    cv2.imshow('b', img2)
    cv2.waitKey(0)
