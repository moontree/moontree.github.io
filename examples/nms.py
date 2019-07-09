"""
greedy nms

data description:

"""

def iou(bbox1, bbox2):
    x11, y11, x21, y21 = bbox1
    x12, y12, x22, y22 = bbox2
    ix = min(x21, x22) - max(x11, x12)
    iy = min(y21, y22) - max(y11, y12)
    if ix < 0 or iy < 0:
        return 0
    a1 = (x21 - x11) * (y21 - y11)
    a2 = (x22 - x12) * (y22 - y12)
    return ix * iy / (a1 + a2 - ix * iy)


def nms(bboxes_with_scores, thre):
    """
    bboxes_with_scores: [[x1, y1, x2, y2], score]
    :param bboxes_with_scores:
    :param thre
    :return:
    """
    bboxes_with_scores.sort(key=lambda x: -x[-1])
    q = []
    cur = None
    for bbox, score in bboxes_with_scores:
        if cur is None:
            cur = bbox
            q.append(cur)
        else:
            if iou(cur, bbox) > thre:
                continue
            else:
                cur = bbox
                q.append(cur)
    return q
