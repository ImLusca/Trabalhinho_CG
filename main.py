
from fnmatch import translate
from operator import concat
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from transformacoes import *

# ### Inicializando janela

glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
largura, altura = [800, 680]
window = glfw.create_window(largura, altura, "joguinho", None, None)
glfw.make_context_current(window)


# ### Capturando eventos de teclado e mouse

posicaoX = 0.0
posicaoY = 0.0
zoomVal = 1.0
teclas = [0] * 4


def camera(window, bt, scanCode, action, mods):
    global teclas
    print(action, bt)

    if (265 < bt < 262):
        return

    if (action == 0):
        teclas[bt - 262] = 0
    else:
        teclas[bt - 262] = 1


glfw.set_key_callback(window, camera)


def zoom(win, dx, dy):
    global zoomVal
    if (dy > 0):
        zoomVal += zoomVal < 20 if 0.005 else 0
    elif (dy < 0):
        zoomVal -= zoomVal > 1.0 if 0.005 else 0


glfw.set_scroll_callback(window, zoom)

vertex_code = """
        attribute vec2 position;

        uniform mat4 mat_transform;
        void main(){
            gl_Position = mat_transform * vec4(position,0.0,1.0);
        }
        """

fragment_code = """
        void main(){
            gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        }
        """


# ### Requisitando slot para a GPU para nossos programas Vertex e Fragment Shaders



# Request a program and shader slots from GPU
program = glCreateProgram()
vertex = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)


# ### Associando nosso código-fonte aos slots solicitados

# Set shaders source
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)


# ### Compilando o Vertex Shader

# Compile shaders
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")


# ### Compilando o Fragment Shader

glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")

# ### Associando os programas compilado ao programa principal
glAttachShader(program, vertex)
glAttachShader(program, fragment)


# ### Linkagem do programa

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


vertices = np.concatenate((quadrado, bumerangue))

# Request a buffer slot from GPU
buffer = glGenBuffers(1)
# Make this buffer the default one
glBindBuffer(GL_ARRAY_BUFFER, buffer)
# Upload data
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)


stride = vertices.strides[0]
offset = ctypes.c_void_p(0)

loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)

glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)


def movimentaCam():
    global posicaoX
    global posicaoY
    if (teclas[0] == 1):
        posicaoX += 0.02
    if (teclas[1] == 1):
        posicaoX -= 0.02
    if (teclas[2] == 1):
        posicaoY += 0.02
    if (teclas[3] == 1):
        posicaoY -= 0.02


def multiplica_matriz(a, b):
    m_a = a.reshape(4, 4)
    m_b = b.reshape(4, 4)
    m_c = np.dot(m_a, m_b)
    c = m_c.reshape(1, 16)
    return c


glfw.show_window(window)


d = 0.0
sentidoTransY = False
sentidoTrans = False
sentidoGiro = False
x = 0.25
y = 0.45
diferenca = 0.009
mat_global_transform = mat_identity()

while not glfw.window_should_close(window):

    glfw.poll_events()

    d -= diferenca

    movimentaCam()

    mat_posicionamento = mat_translate(posicaoX - x, posicaoY - y)
    mat_rotacao = mat_rotate_axis(x, y, d)

    mat_global_transform = multiplica_matriz(
        scale(zoomVal), mat_translate(-posicaoX, -posicaoY))

  
    mat_transformacaoBumerangue = multiplica_matriz(
        mat_global_transform,
        mat_rotacao)

    loc = glGetUniformLocation(program, "mat_transform")

    # glPolygonMode(GL_FRONT_AND_BACK,GL_LINE) ## ative esse comando para enxergar os triângulos
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    objDraw([0, 4], GL_TRIANGLE_STRIP,
            mat_transformacaoBumerangue, [0.7, 0.3, 0.0, 0.0], loc)

    objDraw([4, 9], GL_TRIANGLE_STRIP,
            mat_global_transform, [0.7, 0.3, 0.0, 0.0], loc)

    glfw.swap_buffers(window)

glfw.terminate()
