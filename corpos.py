from OpenGL.GL import *
import glfw
import math

class Corpo:
    def __init__(self, _loc):
        props = []
        vertexModel = []
        cX, cY = 0
        loc = _loc
        cor = [0, 0, 0, 0]
        mat_transformacao = []

    def drawObj(self):
        glUniformMatrix4fv(self.loc[0], 1, GL_TRUE, self.mat_transform)
        glUniform4f(self.loc[1], *self.cor)
        glDrawArrays(mesh, vertex[0], vertex[1])  


