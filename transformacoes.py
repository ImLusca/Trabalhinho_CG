import math
import numpy as np
from OpenGL.GL import *

def mat_translate(x, y):
    return np.array([1.0, 0.0, 0.0, x,
                     0.0, 1.0, 0.0, y,
                     0.0, 0.0, 1.0, 0.0,
                     0.0, 0.0, 0.0, 1.0
                     ], np.float32)


def mat_rotate_axis(x, y, d):
    cos_d = math.cos(d)
    sen_d = math.sin(d)
    resX = x-x*cos_d + y*sen_d
    resY = y-y*cos_d - x*sen_d

    return np.array([cos_d, -sen_d, 0.0, resX,
                     sen_d, cos_d, 0.0, resY,
                     0.0, 0.0, 1.0, 0.0,
                     0.0, 0.0, 0.0, 1.0
                     ], np.float32)


def mat_identity():
    return np.array([1.0, 0.0, 0.0, 0.0,
                     0.0, 1.0, 0.0, 0.0,
                     0.0, 0.0, 1.0, 0.0,
                     0.0, 0.0, 0.0, 1.0
                     ], np.float32)


def scale(s):
    return np.array([s, 0.0, 0.0, 0.0,
                     0.0, s, 0.0, 0.0,
                     0.0, 0.0, 1.0, 0.0,
                     0.0, 0.0, 0.0, 1.0
                     ], np.float32)


def objDraw(vertex, mesh, mat_transform, color, loc):
    glUniformMatrix4fv(loc[0], 1, GL_TRUE, mat_transform)
    glUniform4f(loc[1], *color)
    glDrawArrays(mesh, *vertex)
