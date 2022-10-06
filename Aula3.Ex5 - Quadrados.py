#!/usr/bin/env python
# coding: utf-8

# # Aula3.Ex5 - Quadrados

# ### Primeiro, importamos as bibliotecas necessárias.
# Verifique no código anterior um script para instalar as dependências necessárias (OpenGL e GLFW) antes de prosseguir.

# In[1]:


import math
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np


# ### Inicializando janela

# In[2]:


glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(720, 600, "Quadrados", None, None)
glfw.make_context_current(window)


# ### Capturando eventos de teclado e mouse

# In[3]:


posicaoX = 0.0
posicaoY = 0.0


def mouse_event(window, button, action, mods):
    global posicaoX
    global posicaoY
    print('-------')

    if (glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.RELEASE):
        return

    x, y = glfw.get_cursor_pos(window)
    print(y)
    posicaoX = (x / (720 / 2)) - 1
    posicaoY = -(y / (600 / 2)-1)


glfw.set_mouse_button_callback(window, mouse_event)


vertex_code = """
        attribute vec2 position;

        uniform mat4 mat_transform;
        void main(){
            gl_Position = mat_transform * vec4(position,0.0,1.0);
        }
        """


# ### GLSL para Fragment Shader
#
# No Pipeline programável, podemos interagir com Fragment Shaders.
#
# No código abaixo, estamos fazendo o seguinte:
#
# * void main() é o ponto de entrada do nosso programa (função principal).
# * gl_FragColor é uma variável especial do GLSL. Variáveis que começam com 'gl_' são desse tipo. Nesse caso, determina a cor de um fragmento. Nesse caso é um ponto, mas poderia ser outro objeto (ponto, linha, triangulos, etc).

# In[5]:


fragment_code = """
        void main(){
            gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        }
        """


# ### Requisitando slot para a GPU para nossos programas Vertex e Fragment Shaders

# In[6]:


# Request a program and shader slots from GPU
program = glCreateProgram()
vertex = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)


# ### Associando nosso código-fonte aos slots solicitados

# In[7]:


# Set shaders source
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)


# ### Compilando o Vertex Shader
#
# Se há algum erro em nosso programa Vertex Shader, nosso app para por aqui.

# In[8]:


# Compile shaders
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")


# ### Compilando o Fragment Shader
#
# Se há algum erro em nosso programa Fragment Shader, nosso app para por aqui.

# In[9]:


glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")


# ### Associando os programas compilado ao programa principal

# In[10]:


# Attach shader objects to the program
glAttachShader(program, vertex)
glAttachShader(program, fragment)


# ### Linkagem do programa

# In[11]:


# Build program
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')

# Make program the default program
glUseProgram(program)


# preparando espaço para 4 vértices usando 2 coordenadas (x,y)
quadrado = np.zeros(4, [("position", np.float32, 2)])
# preenchendo as coordenadas de cada vértice
quadrado['position'] = [
    (+0.2, +0.4),
    (+0.3, +0.4),
    (+0.2, +0.5),
    (+0.3, +0.5)
]

bumerangue = np.zeros(10, [("position", np.float32, 2)])

bumerangue['position'] = [
    (+0.75, -0.25),  # vertice 2
    (+0.70, -0.28),
    (+0.50, +0.125),  # vertice 1
    (+0.25, +0.0),  # vertice 3
    (+0.0, +0.25),  # vertice 0
    (+0.0, +0.0625),  # vertice 4
    (-0.50, +0.125),  # vertice 7
    (-0.25, +0.0),  # vertice 5
    (-0.75, -0.25),  # vertice 6
    (-0.70, -0.28)
]

# total_vertices = len(vertices_elipse)
# vertices = np.zeros(total_vertices, [("position", np.float32, 2)])
# vertices['position'] = np.array(vertices_elipse)

# ### Para enviar nossos dados da CPU para a GPU, precisamos requisitar um slot.

# In[14]:


# Request a buffer slot from GPU
buffer = glGenBuffers(2)
# Make this buffer the default one
glBindBuffer(GL_ARRAY_BUFFER, buffer[0])

# Upload data
glBufferData(GL_ARRAY_BUFFER, quadrado.nbytes, quadrado, GL_DYNAMIC_DRAW)

# Make this buffer the default one
glBindBuffer(GL_ARRAY_BUFFER, buffer[1])

# Upload data
glBufferData(GL_ARRAY_BUFFER, bumerangue.nbytes, bumerangue, GL_DYNAMIC_DRAW)

stride = quadrado.strides[0]
offset = ctypes.c_void_p(0)

loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)

glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)


glfw.show_window(window)


d = 0.0
sentidoTransY = False
sentidoTrans = False
sentidoGiro = False
x = 0.25
y = 0.45
diferenca = 0.0


def multiplica_matriz(a, b):
    m_a = a.reshape(4, 4)
    m_b = b.reshape(4, 4)
    m_c = np.dot(m_a, m_b)
    c = m_c.reshape(1, 16)
    return c


lastPx = 1

while not glfw.window_should_close(window):

    glfw.poll_events()

    # if(posicaoX <= -1.2):
    #     sentidoTrans = True
    # elif(posicaoX >= 0.7):
    #     sentidoTrans = False

    # if(sentidoTrans):
    #     posicaoX += 0.01
    # else:
    #     posicaoX -= 0.01

    # if(posicaoY <= -0.3):
    #     sentidoTransY = True
    # elif(posicaoY >= 0.2):
    #     sentidoTransY = False

    # if(sentidoTransY):
    #     posicaoY += 0.003
    # else:
    #     posicaoY -= 0.003

    d -= diferenca

    cos_d = math.cos(d)
    sen_d = math.sin(d)

    a, b = glfw.get_cursor_pos(window)
    posicaoX = (a / (720 / 2)) - 1
    posicaoY = -(b / (600 / 2)-1)

    mat_transla = np.array([1.0, 0.0, 0.0, posicaoX - x,
                            0.0, 1.0, 0.0, posicaoY - y,
                            0.0, 0.0, 1.0, 0.0,
                            0.0, 0.0, 0.0, 1.0
                            ], np.float32)

    resX = x-x*cos_d + y*sen_d
    resY = y-y*cos_d - x*sen_d

    # mat_translate = np.array([1.0, 0.0, 0.0, x,
    #                          0.0, 1.0, 0.0, y,
    #                          0.0, 0.0, 1.0, 0.0,
    #                          0.0, 0.0, 0.0, 1.0
    #                           ], np.float32)

    mat_rotation = np.array([cos_d, -sen_d, 0.0, resX,
                             sen_d, cos_d, 0.0, resY,
                             0.0, 0.0, 1.0, 0.0,
                             0.0, 0.0, 0.0, 1.0
                             ], np.float32)

    # mat_minus_translate = np.array([1.0, 0.0, 0.0, -x,
    #                                 0.0, 1.0, 0.0, -y,
    #                                 0.0, 0.0, 1.0, 0.0,
    #                                 0.0, 0.0, 0.0, 1.0
    #                                 ], np.float32)

    mat_transformation = multiplica_matriz(mat_transla, mat_rotation)

    loc = glGetUniformLocation(program, "mat_transform")
    glUniformMatrix4fv(loc, 1, GL_TRUE, mat_transformation)

    # glPolygonMode(GL_FRONT_AND_BACK,GL_LINE) ## ative esse comando para enxergar os triângulos
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)


    glBindBuffer(GL_ARRAY_BUFFER,buffer[0])
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glBindBuffer(GL_ARRAY_BUFFER,buffer[1])
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 10)
    # glDrawArrays(GL_TRIANGLE_STRIP, 4, 14)

    glfw.swap_buffers(window)

glfw.terminate()


# # Exercício
#
# Modifique esse código para desenhar retângulos.
#
