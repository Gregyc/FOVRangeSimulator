import numpy as np

class Edge:
    # (x1,y1)--------------------(x2,y2)
    # support_vector = (x1,y1)
    # direction_vector = (x2-x1, y2-y1)
    def __init__(self, point_a, point_b):
        self._support_vector = np.array(point_a)
        self._direction_vector = np.subtract(point_b, point_a)

    def get_intersection_point(self, other):
        t = self._get_intersection_parameter(other)
        return None if t is None else self._get_point(t)

    # x = x1 + t (x2-x1)
    # y = y1 + t (y2-y1)
    # _support_vector = (x1,y1)
    # parameter = t
    # direction_vector = (x2-x1, y2-y1)
    def _get_point(self, parameter):
        return self._support_vector + parameter * self._direction_vector

    # x= x1+t1(x2-x1) = x3 + t2 (x4-x3)
    # y= y1+t1(y2-y1) = y3 + t2 (y4-y3)
    # A = ([-(x2-x1), x4-x3]; -(y2-y1),y4-y3)
    # b = ([x1-x3];[y1-y3])
    # get intersection means get t1 and t2
    def _get_intersection_parameter(self, other):
        A = np.array([-self._direction_vector, other._direction_vector]).T
        if np.linalg.matrix_rank(A) < 2:
        	return None
        b = np.subtract(self._support_vector, other._support_vector)
        x = np.linalg.solve(A, b)
        return x[0] if 0 <= x[0] <= 1 and 0 <= x[1] <= 1 else None