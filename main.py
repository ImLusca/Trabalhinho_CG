from audioop import mul
from fnmatch import translate
from operator import concat
from os import remove
import glfw
from OpenGL.GL import *
import random as rnd
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

    if (scanCode == 36 and action == 1 and not shurikenAr):
        p = posBola(1)
        lancamentoBola(p[0], p[1])

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


def F(u, odd, r):
    if odd:
        x = r * math.cos(u)
        y = r * math.sin(u)
    else:
        x = r * 1/2 * math.cos(u)
        y = r * 1/2 * math.sin(u)

    return [x, y]


def retornaEstrela(nv, r):
    PI = 3.141592
    step = (PI * 2)/(nv - 2)
    r = 0.045
    vertices_elipse = np.zeros(nv, [("position", np.float32, 2)])

    vertices_elipse[0] = [0, 0]

    for i in range(0, nv - 2):

        u = i * step
        if (i % 2 == 0):
            p = F(u, True, r)
        else:
            p = F(u, False, r)

        vertices_elipse[i + 1] = p
    vertices_elipse[nv - 1] = vertices_elipse[1]

    print(vertices_elipse[nv - 1], vertices_elipse[1])

    return vertices_elipse


nvEstrela = 16
r = 0.2
vertices_estrela = retornaEstrela(nvEstrela, r)


def geraRetangulo(x, y, tx, ty):
    quadrado = np.zeros(4, [("position", np.float32, 2)])
    quadrado['position'] = [
        (x, y),
        (x, y+ty),
        (x+tx, y),
        (x+tx, y+ty)
    ]
    return quadrado


terreno = np.zeros(4, [("position", np.float32, 2)])

terreno["position"] = [
    (-10.0, -10.0),
    (-10.0, 0),
    (10.0, -10.0),
    (10.0, 0)
]

terreno2 = np.zeros(4, [("position", np.float32, 2)])

terreno2["position"] = [
    (-10.0, -10.0),
    (-10.0, -0.3),
    (10.0, -10.0),
    (10.0, -0.3)
]


def retornaBola(x, y, r, nv):
    circle = np.zeros(nv, [("position", np.float32, 2)])
    dPi = 6.28318
    circle[0] = [x, y]
    for i in range(nv - 1):
        cX = x + (r * math.cos(i * dPi/(nv - 2)))
        cY = y + (r * math.sin(i * dPi/(nv - 2)))
        circle[i + 1] = [cX, cY]

    return circle


nvBall = 15
raioBola = 0.035
ball = retornaBola(0, 0, raioBola, nvBall)


def retornoFaixa(r):
    faixa = np.zeros(4, [("position", np.float32, 2)])
    dPI = 3.141592

    cX = r * math.cos(dPI/4.5)
    cY = r * math.sin(dPI/4.5)
    faixa[0] = [cX, cY]
    cX = r * math.cos((dPI/3))
    cY = r * math.sin((dPI/3))
    faixa[1] = [cX, cY]
    cX = r * math.cos((dPI/1.28))
    cY = r * math.sin((dPI/1.28))
    faixa[2] = [cX, cY]
    cX = r * math.cos((dPI/1.5))
    cY = r * math.sin((dPI/1.5))
    faixa[3] = [cX, cY]

    return faixa


vertices = np.concatenate(
    (terreno, terreno2, ball, vertices_estrela, retornoFaixa(raioBola)))['position']

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
    global ninjaPulando
    velocidadeCam = 0.04
    if (teclas[0] == 1):
        posicaoX += velocidadeCam
    if (teclas[1] == 1):
        posicaoX -= velocidadeCam
    if (teclas[3] == 1 and posicaoY <= 0.010):
        ninjaPulando = True

    if ninjaPulando and posicaoY < limitePulo:
        posicaoY += velocidadePulo
    elif posicaoY >= limitePulo:
        ninjaPulando = False

    if not ninjaPulando and posicaoY > 0.0:
        posicaoY -= velocidadePulo


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


def lancamentoBola(x, y):
    global aBola
    global shurikenAr
    H = math.sqrt(pow(x, 2) + pow(y, 2))
    exp = (pow(H, 2) + pow(x, 2) - pow(y, 2)) / (2*H*x)
    aBola = math.acos(exp)
    shurikenAr = True


def calcLimiteLancamento():
    global shurikenAr
    global dshuriken
    if (dshuriken >= 1.4):
        shurikenAr = False
        dshuriken = raioLancamento


def desenhaCometa(listaCometa):
    for i in listaCometa:
        i[1] -= 0.0015
        mat = mat_translate(i[0], i[1])
        mat = multiplica_matriz(mat_global_transform, mat)
        objDraw([8, nvBall], GL_TRIANGLE_FAN,
                mat, [0.8, 0.8, 0.8, 0.0], [loc, loc_color])


def retornaCometa():
    if (rnd.randint(1, 100) == 2):
        xPos = rnd.uniform(-1, 1)
        return [xPos, 1.2]
    return None


def desenhaNinja():
    objDraw([8, nvBall], GL_TRIANGLE_FAN,
            multiplica_matriz(scale(1.45), mat_translate(0, 0)), [1, 0.77, 0.61, 0.0], [loc, loc_color])
    objDraw([8, nvBall], GL_TRIANGLE_FAN,
            multiplica_matriz(scale(1.45), mat_translate(0, -0.05)), [0, 0, 0, 0.0], [loc, loc_color])
    objDraw([8 + nvBall + nvEstrela, 4], GL_TRIANGLE_STRIP,
            multiplica_matriz(scale(1.45), mat_translate(0, 0)), [0, 0, 0, 0.0], [loc, loc_color])


def lancamentoShuriken():
    global dshuriken
    global diferenca
    if (shurikenAr):
        dshuriken += 0.023
        diferenca = 0.3
        calcLimiteLancamento()
        p = [math.cos(aBola) * dshuriken, math.sin(aBola) * dshuriken]
        for cometa in listaCometa:
            if (calcColisao(*p, *cometa)):
                listaCometa.remove(cometa)
    else:
        diferenca = 0.009
        p = posBola(raioLancamento)
    return p


def distanciaEuclidiana(x1, y1, x2, y2):
    return math.sqrt(pow(x1 - x2, 2) + math.sqrt(pow(y1 - y2, 2)))


def calcColisao(xBola, yBola, xCometa, yCometa):
    return distanciaEuclidiana(xBola, yBola, xCometa - posicaoX, yCometa) < raioBola * 3


d = 0.0
raioLancamento = 0.1
shurikenAr = False
ninjaPulando = False
limitePulo = 0.2
velocidadePulo = 0.015
aBola = 0.0
dshuriken = raioLancamento
diferenca = 0.009
mat_global_transform = mat_identity()
listaCometa = []

while not glfw.window_should_close(window):

    glfw.poll_events()

    d -= diferenca

    movimentaCam()
    auxCometa = retornaCometa()

    mat_global_transform = multiplica_matriz(
        scale(zoomVal), mat_translate(-posicaoX, -posicaoY))

    loc = glGetUniformLocation(program, "mat_transform")

    # ative esse comando para enxergar os triângulos
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0.1884313, 0.189431, 0.42372, 1.0)

    if (auxCometa != None):
        listaCometa.append(auxCometa)
    if (len(listaCometa) > 0):
        desenhaCometa(listaCometa)

    posShuriken = lancamentoShuriken()

    for cometa in listaCometa:
        if (cometa[1] < 0.0):
            listaCometa.remove(cometa)

    a, b = vertices_estrela['position'][0]

    mat_transformacaoEstrela = mat_rotate_axis(a, b, d)

    mat_transformacaoEstrela = multiplica_matriz(
        mat_translate(*posShuriken), mat_rotate_axis(a, b, d))

    objDraw([0, 4], GL_TRIANGLE_STRIP,
            mat_global_transform, [0.2, 0.8, 0.05, 0.0], [loc, loc_color])

    objDraw([4, 4], GL_TRIANGLE_STRIP,
            mat_global_transform, [0.8, 0.6, 0.05, 0.0], [loc, loc_color])

    # objDraw([8, nvBall], GL_TRIANGLE_FAN,
    #         multiplica_matriz(mat_global_transform, mat_rotBall), [0.7, 0.1, 0.1, 0.0], [loc, loc_color])

    objDraw([23, nvEstrela], GL_TRIANGLE_FAN,
            mat_transformacaoEstrela, [0.7, 0.1, 0.1, 0.0], [loc, loc_color])

    desenhaNinja()

    glfw.swap_buffers(window)

glfw.terminate()
