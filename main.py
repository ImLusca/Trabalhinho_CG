
from calendar import c
from cmath import sqrt
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

    x, y = glfw.get_cursor_pos(window)
    x = x / (largura/2) - 1
    y = y / (altura/2) - 1

    print(x, y)
    p = posBola(1)
    print(p[0], p[1])
    if (265 < bt or bt < 262):
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
        zoomVal -= zoomVal > 1.00 if 0.005 else 0


glfw.set_scroll_callback(window, zoom)

vertex_code = """
        attribute vec2 position;

        uniform mat4 mat_transform;
        void main(){
            gl_Position = mat_transform * vec4(position,0.0,1.0);
        }
        """

fragment_code = """
        uniform vec4 color;
        void main(){
            gl_FragColor = color;
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
    (0.4, 0.6),
    (0.4, 0.8),
    (0.6, 0.6),
    (0.6, 0.8)
]

terreno = np.zeros(4, [("position", np.float32, 2)])

terreno["position"] = [
    (-10.0, -10.0),
    (-10.0, 0.0),
    (10.0, -10.0),
    (10.0, 0.0)
]


def retornaBola(x, y, r, nv):
    circle = np.zeros(nv, [("position", np.float32, 2)])
    dPi = 6.28318
    for i in range(nv):
        cX = x + (r * math.cos(i * dPi/nv))
        cY = y + (r * math.sin(i * dPi/nv))
        circle[i] = [cX, cY]
    return circle


ball = retornaBola(0, 0, 0.035, 10)

vertices = np.concatenate((quadrado, terreno, ball))['position']
print(vertices)

# Request a buffer slot from GPU
buffer = glGenBuffers(1)
# Make this buffer the default one
glBindBuffer(GL_ARRAY_BUFFER, buffer)
# Upload data
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)


stride = vertices.strides[0]
offset = ctypes.c_void_p(0)

loc = glGetAttribLocation(program, "position")
loc_color = glGetUniformLocation(program, "color")
glEnableVertexAttribArray(loc)
glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)


def movimentaCam():
    global posicaoX
    global posicaoY
    velocidadeCam = 0.04
    if (teclas[0] == 1):
        posicaoX += velocidadeCam
    if (teclas[1] == 1):
        posicaoX -= velocidadeCam
    if (teclas[2] == 1):
        posicaoY -= velocidadeCam
    if (teclas[3] == 1):
        posicaoY += velocidadeCam


def multiplica_matriz(a, b):
    m_a = a.reshape(4, 4)
    m_b = b.reshape(4, 4)
    m_c = np.dot(m_a, m_b)
    c = m_c.reshape(1, 16)
    return c


glfw.show_window(window)


def posBola(r):
    x, y = glfw.get_cursor_pos(window)
    x = x / (largura/2) - 1
    y = y / (altura/2) - 1
    H = math.sqrt(pow(x, 2) + pow(y, 2))

    if (y >= 0):
        if (x > 0):
            return [r, 0]
        else:
            return [-r, 0]

    if ((2*H*x) == 0):
        return [0, 0]

    exp = (pow(H, 2) + pow(x, 2) - pow(y, 2)) / (2*H*x)
    a = math.acos(exp)
    return [math.cos(a) * r, math.sin(a) * r]


def calcTrajetoria(x, y, anguloLance, forca):
    vet_vert = forca * math.sin(anguloLance)
    vet_hor = forca * math.cos(anguloLance)
    gravidade = 0.01
    resVert = 0
    i = 0
    pontosX, pontosY = []
    while vet_hor >= 0:
        i += 1
        vet_vert -= gravidade
        vet_h = vet_hor * i
        pontosX.append(x + vet_vert)
        pontosY.append(y + vet_h)
    return pontosX, pontosY


d = 0.0
sentidoTransY = False
sentidoTrans = False
sentidoGiro = False
x = 0.5
y = 0.7
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

    # ative esse comando para enxergar os triângulos
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    objDraw([0, 4], GL_TRIANGLE_STRIP,
            mat_transformacaoBumerangue, [0.9, 0.5, 0.0, 0.0], [loc, loc_color])

    p = posBola(0.4)
    mat_rotBall = mat_translate(p[0], p[1])
    objDraw([4, 4], GL_TRIANGLE_STRIP,
            mat_global_transform, [0.2, 0.8, 0.05, 0.0], [loc, loc_color])

    objDraw([8, 10], GL_TRIANGLE_FAN,
            multiplica_matriz(mat_global_transform, mat_rotBall), [0.7, 0.1, 0.1, 0.0], [loc, loc_color])

    glfw.swap_buffers(window)

glfw.terminate()
