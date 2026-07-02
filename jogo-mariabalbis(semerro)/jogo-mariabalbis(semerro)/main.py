from dataclasses import dataclass
import pyxel
import math
import random

#CORES permitidas: 
#COLOR_BLACK
#COLOR_NAVY
#COLOR_PURPLE
#COLOR_GREEN
#COLOR_BROWN
#COLOR_DARK_BLUE
#COLOR_LIGHT_BLUE
#COLOR_WHITE
#COLOR_RED
#COLOR_ORANGE
#COLOR_YELLOW
#COLOR_LIME
#COLOR_CYAN
#COLOR_GRAY
#COLOR_PINK
#COLOR_PEACH

#Classe que define as mercadorias para pontuação
#Devem ser coletadas pelo jogador
@dataclass
class Merch:
    x:int
    y:int
    points:int

    def get_color(self):
        match self.points:
            case 10:
                return pyxel.COLOR_CYAN
            case 20:
                return pyxel.COLOR_LIME
            case 40:
                return pyxel.COLOR_PINK
            case 80:
                return pyxel.COLOR_PEACH
            case -10:
                return pyxel.COLOR_DARK_BLUE
            case -30:
                return pyxel.COLOR_ORANGE
            case -50:
                return pyxel.COLOR_RED
            case _:
                return "Unknown Status"

# Classe para as informações das naves
@dataclass
class Ship:
    x:int
    y:int
    rotation: float = 0 #angulo de rotação (radianos)
    rotation_dir: int = 0 # -1=esquerda, 0=sem rotação, 1=direita
    acceleration: int = 0
    exploded:bool = False
    points:int = 0
    lives:int = 3
    
##########################
### Definição de constantes para configuração
##########################
#Constantes para configuração do movimento das naves
SHIP_RADIUS = 8
ROTATION_SPEED = 0.03
TOP_SPEED = 10
MAX_ACCELERATION = 2
ACCELERATION_DELTA = 0.02
#Constantes para definição da estrela
STAR_POSITION = { 'x': 150, 'y': 150 }
STAR_SCALE = 3
STAR_RADIUS = 8 * STAR_SCALE
STAR_COLOR = pyxel.COLOR_PINK

#Definições de pontuação para distribuição aleatória
POINTS = [10,20,-10,40,-30,80,-50]
WEIGHTS = [10,11,20,21,40,41,42]
WEIGHT_BUDGET = 1000

#Mercadorias que podem ser coletadas pelo jogador
MERCHS_IN_PLAY = []

auditoria = { 'dv':{},'np':{} }

#################################
### Funções para o controle da movimentação das naves
#################################
def set_rotation(ship, direction) :
    if ship.rotation_dir == direction :
        return
    if ship.rotation_dir == -direction :
        ship.rotation_dir = 0
    else:
        ship.rotation_dir = direction

def unset_rotation(ship, direction) :
    if ship.rotation_dir == direction :
        ship.rotation_dir = 0
    elif ship.rotation_dir == -direction :
        return
    
def rotate_ship(ship):
    if ship.rotation_dir != 0:
        ship.rotation += ship.rotation_dir*ROTATION_SPEED

def move_ship(ship):
    #TO-DO: Implementar gravidade da estrela puxando a nave
    #Propulsores da nave
    # Vetor que determina a direção de movimento da nave
    direction_vec = { 'x': math.cos(ship.rotation), 'y': math.sin(ship.rotation) }
    auditoria['dv']= direction_vec
    
    dx = STAR_POSITION['x'] - ship.x
    dy = STAR_POSITION['y'] - ship.y

    distancia = math.sqrt(dx**2 + dy**2)

    G = 0.08

    if distancia != 0:
        gravidade_x = (dx/distancia) * G
        gravidade_y = (dy/distancia) * G
    else:
        gravidade_x = 0
        gravidade_y = 0

    ship.x += direction_vec['x'] * ship.acceleration + gravidade_x
    ship.y += direction_vec['y'] * ship.acceleration + gravidade_y

def move_scraps():

    G = 0.04

    for scrap in MERCHS_IN_PLAY:

        dx = STAR_POSITION['x'] - scrap.x
        dy = STAR_POSITION['y'] - scrap.y

        distancia = math.sqrt(dx**2 + dy**2)

        if distancia != 0:
            scrap.x += (dx/distancia) * G
            scrap.y += (dy/distancia) * G
            
def set_acceleration(ship, magnitude):
    ship.acceleration += magnitude * ACCELERATION_DELTA
    if ship.acceleration > MAX_ACCELERATION :
        ship.acceleration = MAX_ACCELERATION
    elif (ship.acceleration < 0):
        ship.acceleration = 0

#####################
#### Funções de inicialização das Mercadorias (pontos)
#####################
# Seleção aleatória com base em pesos
def select_points():
    total = 0
    for w in WEIGHTS:
        total += w
    # Número aleatório [1, total]
    rd = random.randint(1,total)
    cursor = 0
    for i in range(len(WEIGHTS)):
        cursor += WEIGHTS[i]
        if (cursor >= rd):
            return (POINTS[i],WEIGHTS[i])
    return -10
    
def spawn_scrap():
   budget = WEIGHT_BUDGET
   while budget > 0:
       p,w = select_points()
       # Cria a mercadoria em uma posição aleatória dentro do mapa (entre 0 e 300)
       #TO-DO: criar lógica para evitar que seja criada muito próxima da estrela
       #TO-DO: Criar lógica para espalhar melhor os pontos no mapa
       scrap = Merch(random.randint(0,300),random.randint(0,300),p)
       MERCHS_IN_PLAY.append(scrap)
       budget -= w

###########################
#### Funções para verificação de colisões
###########################

#Verifica colisões das mercadorias
def check_scrap_collision(ship):
    #TO-DO: Verifica se a nave encostou nas cargas
    #TO-DO: Verifica se as cargas encostaram na estrela
    #RETORNA: Lista de Merchs pegos pela nave, lista de Merchs engolidos pela estrela

    remover = []

    for scrap in MERCHS_IN_PLAY:
        dx = scrap.x - ship.x
        dy = scrap.y - ship.y
        distancia = math.sqrt(dx**2 + dy**2)

        if distancia <= SHIP_RADIUS:
            ship.points += scrap.points
            remover.append(scrap)

    for scrap in remover:
        MERCHS_IN_PLAY.remove(scrap)

    remover2 = []

    for scrap in MERCHS_IN_PLAY:

        dx = STAR_POSITION['x'] - scrap.x
        dy = STAR_POSITION['y'] - scrap.y

        distancia = math.sqrt(dx**2 + dy**2)

        if distancia <= STAR_RADIUS:
            remover2.append(scrap)

    for scrap in remover2:
        MERCHS_IN_PLAY.remove(scrap)
        
    return remover, remover2
    
# Verifica colisões da nave
def check_collisions(ship):

    dx = STAR_POSITION['x'] - ship.x
    dy = STAR_POSITION['y'] - ship.y

    distancia = math.sqrt(dx**2 + dy**2)

    if distancia <= STAR_RADIUS + SHIP_RADIUS:
        ship.lives -= 1
        ship.x = 50
        ship.y = 50
        ship.acceleration = 0
        
    if ship.x < 0 or ship.x > 300 or ship.y < 0 or ship.y > 300:
        ship.lives -= 1
        ship.x = 50
        ship.y = 50
        ship.acceleration = 0
    
    return

# Desenha um coração simples (duas bolinhas em cima + um triângulo embaixo)
def draw_heart(x, y, color):
    pyxel.circ(x + 2, y + 2, 2, color)
    pyxel.circ(x + 6, y + 2, 2, color)
    pyxel.tri(x, y + 3, x + 8, y + 3, x + 4, y + 8, color)

# Desenha um coração para cada vida restante do jogador
def draw_lives(x, y, lives):
    for i in range(lives):
        draw_heart(x + i * 10, y, pyxel.COLOR_RED)

# Desenha a legenda explicando quantos pontos cada cor de mercadoria vale.
# Reaproveita o Merch.get_color() para garantir que a cor mostrada aqui
# seja sempre a mesma usada de verdade no jogo.
def draw_legend(x, y):
    pyxel.text(x, y, "PONTOS", pyxel.COLOR_WHITE)
    for i, pontos in enumerate(sorted(POINTS, reverse=True)):
        linha_y = y + 8 + i * 8
        cor = Merch(0, 0, pontos).get_color()
        pyxel.circ(x + 2, linha_y + 2, 2, cor)
        texto = f"+{pontos}" if pontos > 0 else str(pontos)
        pyxel.text(x + 8, linha_y, texto, pyxel.COLOR_WHITE)

######################
### Classe principal da game engine
######################
class App:
    c_needle = Ship(50,50)
    c_wedge = Ship(250,250)

    def __init__(self):
        pyxel.init(300, 300)
        pyxel.load("my_resource.pyxres")
        self.x = 0
        spawn_scrap()
        pyxel.run(self.update, self.draw)
        
    # Processa a entrada de teclado do usuário
    def processa_teclado(self):
        if pyxel.btn(pyxel.KEY_W):
            set_acceleration(self.c_needle, 1)
        elif pyxel.btn(pyxel.KEY_S):
            set_acceleration(self.c_needle, -1)
        if pyxel.btn(pyxel.KEY_A):
            set_rotation(self.c_needle, -1)
        elif pyxel.btn(pyxel.KEY_D):
            set_rotation(self.c_needle, 1)

        if not pyxel.btn(pyxel.KEY_A):
            unset_rotation(self.c_needle, -1)
        if not pyxel.btn(pyxel.KEY_D):
            unset_rotation(self.c_needle, 1)

    #Atualiza as informações do jogo ANTES de desenhar cada frame
    # 1. Verifica se há alguma tecla pressionada
    # 2. Aplica rotação na Nave
    # 3. Aplica o movimento da nave
    def update(self):
        self.processa_teclado()
        rotate_ship(self.c_needle)
        move_ship(self.c_needle)
        move_scraps()
        check_collisions(self.c_needle)
        check_scrap_collision(self.c_needle)

    #Faz o desenho da tela do jogo
    def draw(self):
        if self.c_needle.lives <= 0:
            pyxel.cls(0)
            pyxel.text(100, 150, "GAME OVER", pyxel.COLOR_RED)
            pyxel.text(100, 160, f"Pontos: {self.c_needle.points}", pyxel.COLOR_WHITE)
            return
        pyxel.cls(0)
        needle = self.c_needle
        wedge = self.c_wedge
        # Estrela no centro da tela
        pyxel.circ(STAR_POSITION['x'], STAR_POSITION['y'], STAR_RADIUS, STAR_COLOR)
        # Nave do Jogador 1 (Needle)
        pyxel.blt(needle.x, needle.y, 0, 8, 8, 16, 16, rotate=math.degrees(needle.rotation)+90, colkey=0)
        for scrap in MERCHS_IN_PLAY:
            pyxel.circ(scrap.x, scrap.y, 2, col=scrap.get_color())
        #pyxel.text(48, 100, "Pyxel Code Maker", pyxel.rndi(1, 15))
        draw_lives(10, 5, needle.lives)
        pyxel.text(10, 16, f"Pontos: {needle.points}", pyxel.COLOR_WHITE)
        draw_legend(250, 5)
        # Remover Texto Abaixo. Usado apenas para auxiliar no desenvolvimento
        #pyxel.text(10, 25, f"DV: {auditoria['dv']}", pyxel.COLOR_WHITE)
        #pyxel.text(10, 35, f"Need: x:{needle.x} y:{needle.y} r:{needle.rotation}", pyxel.COLOR_WHITE)
    
App()
