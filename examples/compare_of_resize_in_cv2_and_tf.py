import tensorflow as tf
import numpy as np
import cv2
from PIL import Image


def compute_lerp(top_left, top_right, bottom_left, bottom_right, x_lerp, y_lerp):
    """
    calculate the final value according to corner values and lerp using bi-linear
    :param top_left: ori image value of top left corner
    :param top_right: ori image value of top right corner
    :param bottom_Left: ori image value of bottom left corner
    :param bottom_right: ori image value of bottom right corner
    :param x_lerp: x offset in [0, 1] responding to top left corner index
    :param y_lerp: y offset in [0, 1] responding to top left corner index
    :return:
    """
    top = top_left + (top_right - top_left) * x_lerp
    bottom = bottom_left + (bottom_right - bottom_left) * x_lerp
    return top + (bottom - top) * y_lerp


def calculate_resize_scale(in_size, out_size, align_corners=False):
    """
    calculate resize factor
    :param in_size:
    :param out_size:
    :param align_corners:
    :return:
    """
    if align_corners and out_size > 1:
        return (in_size - 1) / (out_size - 1)
    else:
        return in_size / out_size


def compute_interpolation_weights(out_size, in_size, scale):
    """
    calculate interpolation in tensorflow
    :param out_size:
    :param in_size:
    :param scale:
    :return:
    """
    # lower, upper, lerp
    res = [[0, 0, 0] for _ in range(out_size + 1)]
    for i in range(out_size - 1, -1, -1):
        val = i * scale
        res[i][0] = int(val)
        res[i][1] = min(res[i][0] + 1, in_size - 1)
        res[i][2] = val - int(val)
    return res


def cv_compute_interpolation_weights(out_size, in_size, scale):
    """
    calculate interpolation in opencv
    :param out_size:
    :param in_size:
    :param scale:
    :return:
    """
    # lower, upper, lerp
    res = [[0, 0, 0] for _ in range(out_size + 1)]
    res[-1] = [0, 0]
    for i in range(out_size - 1, -1, -1):
        val = (i + 0.5) * scale - 0.5
        res[i][0] = max(0, int(val))
        res[i][1] = min(res[i][0] + 1, in_size - 1)
        res[i][2] = max(0, val - int(val))
    return res


def print_image(matrix):
    for r in matrix:
        for c in r:
            print("%.2f" % c, end=' ')
        print()


interplation_map = {
    'cv': cv_compute_interpolation_weights,
    'tf': compute_interpolation_weights
}


def resize_simulator_bi_linear(image, target_size, mode):
    """
    simulator of resize
    :param image: image value of [h, w, 1]
    :param target_size: target size in format (w, h)
    :param mode: 'cv' or 'tf'
    :return:
    """
    assert mode in interplation_map, "mode should be cv or tf"
    ow, oh = target_size
    iw, ih = np.shape(image)[:2]
    h_scale = calculate_resize_scale(ih, oh)
    w_scale = calculate_resize_scale(iw, ow)
    w_lerp = interplation_map[mode](ow, iw, w_scale)
    h_lerp = interplation_map[mode](oh, ih, h_scale)
    res = [[0 for _ in range(ow)] for _ in range(oh)]
    for r in range(oh):
        for c in range(ow):
            yinfo = h_lerp[r]
            xinfo = w_lerp[c]
            res[r][c] = compute_lerp(
                image[yinfo[0]][xinfo[0]],
                image[yinfo[0]][xinfo[1]],
                image[yinfo[1]][xinfo[0]],
                image[yinfo[1]][xinfo[1]],
                xinfo[2],
                yinfo[2]
            )
    return res


def pil_resize(image, target_size, mode):
    img = Image.fromarray(image[:, :, 0])
    img = img.resize(target_size, resample=Image.BILINEAR)
    return np.array(img)


def compare():
    resize_shape = (4, 4)
    image = np.ones([1, 3, 3, 1], dtype=np.float32)
    image[0][0][0][0] = 5.
    image[0][1][1][0] = 5.
    image[0][2][2][0] = 5.
    for r in image[0]:
        print(r[:,0])
    inputs = tf.constant(image)
    sess = tf.Session()
    outputs = tf.image.resize_bilinear(inputs, resize_shape)
    outputs = tf.reshape(outputs, resize_shape)
    print('---- using tf.image ----')
    print_image(sess.run(outputs))
    print('---- using tf simulator ----')
    print_image(resize_simulator_bi_linear(image[0], resize_shape, 'tf'))
    print('---- using cv simulator ----')
    print_image(resize_simulator_bi_linear(image[0], resize_shape, 'cv'))
    print('---- using opencv ----')
    print_image(cv2.resize(image[0], resize_shape, interpolation=cv2.INTER_LINEAR))
    # print_image(cv2.resize(image[0], resize_shape, interpolation=cv2.INTER_CUBIC))
    # print_image(cv2.resize(image[0], resize_shape, interpolation=cv2.INTER_NEAREST))
    print('---- using pillow ----')
    print_image(pil_resize(image[0], resize_shape, ''))

if __name__ == "__main__":
    compare()
