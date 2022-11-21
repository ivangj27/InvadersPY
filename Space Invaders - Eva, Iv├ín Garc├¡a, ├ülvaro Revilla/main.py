import pygame
from pygame import mixer
from pygame.locals import *
import random

# Configuración general
pygame.mixer.pre_init(44100, -16, 2, 512)  # (freq 44100 x def., -16 x def., canal 2 x def., tamaño buffer lo reducimos)
pygame.font.init()  # Inicializa el módulo font para las fuentes
mixer.init()
pygame.init()  # Inicializa los módulos pygame y es requerido para cualquier tipo de juego

# FPS a los que correrá el juego
reloj = pygame.time.Clock()
fps = 60

# Creación de ventana (Tamaño, titulo):
ancho_pantalla = 600
largo_pantalla = 700

pantalla = pygame.display.set_mode((ancho_pantalla, largo_pantalla))  # display surface
pygame.display.set_caption("Space Invanders")  # Nombre ventana

# Definimos variables de fuentes
#                        (Path/Nombre fuente, tamaño)
fuente30 = pygame.font.Font("Fuentes/Goldman-Regular.ttf", 30)
fuente40 = pygame.font.Font("Fuentes/Goldman-Regular.ttf", 40)

# Carga de ficheros de sonido de explosión y de disparo del juego
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)
explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)
laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

# Definición de columnas y filas del array de aliens
filas = 5
columnas = 5
alien_enfriamiento = 1000  # Tiempo de enfriamiento entre disparos de los alienígenas
ultimo_disparo_alien = pygame.time.get_ticks()
cuenta_atras = 3
cuenta_final = pygame.time.get_ticks()
game_over = 0  # 0 es estado neutro, 1 para cuando el jugador ha ganado, -1 para cuando el jugador ha perdido

# Colores a utilizar
rojo = (255, 0, 0)
verde = (0, 255, 0)
blanco = (255, 255, 255)

# Carga de imagen de fondo
fondo = pygame.image.load("img/bg.png")


def dibujar_fondo():
    pantalla.blit(fondo, (0, 0))


# Función de creación del texto en pantalla
def dibujar_texto(text, font, text_col, x, y):
    img = font.render(text, True, text_col,'black') # Añadimos el color negro como fondo de letreros para que se visualize sobre los demás elementos

    pantalla.blit(img, (x, y))


# Creación de la clase de la nave del jugador
class Nave(pygame.sprite.Sprite):

    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vida_inicio = health
        self.vida_restante = health
        self.ultimo_disparo = pygame.time.get_ticks()

    def update(self):
        # Velocidad de movimiento base del jugador
        velocidad = 8
        # Tiempo de enfriamiento entre disparos del jugador en milisegundos
        enfriamiento = 500
        game_over = 0

        # Controles de movimiento del jugador
        tecla = pygame.key.get_pressed()
        if tecla[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= velocidad
        if tecla[pygame.K_RIGHT] and self.rect.right < ancho_pantalla:
            self.rect.x += velocidad

        tiempo_actual = pygame.time.get_ticks()
        # Control de disparo del jugador
        if tecla[pygame.K_SPACE] and tiempo_actual - self.ultimo_disparo > enfriamiento:
            laser_fx.play()
            bala = Balas(self.rect.centerx, self.rect.top)
            balas_grupo.add(bala)
            self.ultimo_disparo = tiempo_actual

        self.mask = pygame.mask.from_surface(self.image)

        # Barra de vida
        pygame.draw.rect(
            pantalla, rojo, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15)
        )
        if self.vida_restante > 0:
            pygame.draw.rect(
                pantalla,
                verde,
                (
                    self.rect.x,
                    (self.rect.bottom + 10),
                    int(self.rect.width * (self.vida_restante / self.vida_inicio)),
                    15,
                ),
            )

        elif self.vida_restante <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_grupo.add(explosion)
            self.kill()
            game_over=-1
            
   
        if pygame.sprite.spritecollide(
                self, grupo_aliens, False, pygame.sprite.collide_mask
        ):
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_grupo.add(explosion)
            self.kill()
            game_over = -1
            
        return game_over


# Creación de la clase que define los disparos
class Balas(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, grupo_aliens, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_grupo.add(explosion)


# Creación de clase para los aliens
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien1.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.mover_direccion = 1

    def update(self):
        self.rect.x += self.mover_direccion
        if self.rect.x + self.rect.width > ancho_pantalla - self.rect.width or self.rect.x < 0:
                self.mover_direccion *= -1
                self.rect.y += 50

        
      


# Creación de las balas de los aliens
class Balas_Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > largo_pantalla:
            self.kill()
        if pygame.sprite.spritecollide(
                self, naves_grupo, False, pygame.sprite.collide_mask
        ):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            nave.vida_restante -= 1
            nave.visibilidad_vida = True
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_grupo.add(explosion)


# Clase para la explosión tras la muerte de un alien
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.indice = 0
        self.image = self.images[self.indice]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.contador = 0

    def update(self):
        explosion_velocidad = 3
        # Actualizar la animación de la explosión
        self.contador += 1

        if self.contador >= explosion_velocidad and self.indice < len(self.images) - 1:
            self.contador = 0
            self.indice += 1
            self.image = self.images[self.indice]

        # Si la animacion ha terminado borrar la explosion
        if self.indice >= len(self.images) - 1 and self.contador >= explosion_velocidad:
            self.kill()


# Grupos de sprites
naves_grupo = pygame.sprite.Group()
balas_grupo = pygame.sprite.Group()
grupo_aliens = pygame.sprite.Group()
aliens_balas_grupo = pygame.sprite.Group()
explosion_grupo = pygame.sprite.Group()


# Función para generar los alienígenas en las filas y columnas definidas
def crear_aliens():
    for fila in range(filas):
        for objeto in range(columnas):
            alien = Aliens(100 + objeto * 100, 100 + fila * 70)
            grupo_aliens.add(alien)


crear_aliens()

# Creación del jugador
nave = Nave(int(ancho_pantalla / 2), largo_pantalla - 100, 3)
naves_grupo.add(nave)

# Bucle principal del juego donde ejecutaremos las funciones:
inicio = True
while inicio:

    reloj.tick(fps)

    # Se dibuja el fondo
    dibujar_fondo()
    dibujar_texto(
        "SPACE INVADERS",
        fuente40,
        blanco,
        int(ancho_pantalla / 2 - 185),
        int(20),
    )
    
    # Actualización de las explosiones
    explosion_grupo.update()

    # Se dibujan los grupos de sprites en pantalla
    naves_grupo.draw(pantalla)
    balas_grupo.draw(pantalla)
    grupo_aliens.draw(pantalla)
    aliens_balas_grupo.draw(pantalla)
    explosion_grupo.draw(pantalla)

    
    if cuenta_atras == 0:
        # Se crean aleatoriamente los disparos de los aliens
        tiempo_actual = pygame.time.get_ticks()
        if (
                tiempo_actual - ultimo_disparo_alien > alien_enfriamiento
                and len(aliens_balas_grupo) < 5
                and len(grupo_aliens) > 0
        ):
            atacando_alien = random.choice(grupo_aliens.sprites())
            alien_bala = Balas_Aliens(
                atacando_alien.rect.centerx, atacando_alien.rect.bottom
            )
            aliens_balas_grupo.add(alien_bala)
            ultimo_disparo_alien = tiempo_actual

        # Comprobación de condición de victoria
        if len(grupo_aliens) == 0:
            game_over = 1

        if game_over == 0:
            # Actualización del jugador en pantalla
            game_over = nave.update()

            # Actualización de los sprites
            balas_grupo.update()
            grupo_aliens.update()
            aliens_balas_grupo.update()

        else:
            if game_over == -1:
                dibujar_texto(
                    "HAS PERDIDO!",
                    fuente40,
                    blanco,
                    int(ancho_pantalla / 2 - 150),
                    int(largo_pantalla / 2 + 50),
                )
                
            if game_over == 1:
                dibujar_texto(
                    "HAS GANADO!",
                    fuente40,
                    blanco,
                    int(ancho_pantalla / 2 - 150),
                    int(largo_pantalla / 2 + 50),
                )
            

    if cuenta_atras > 0:
        dibujar_texto(
            "PREPÁRATE!",
            fuente40,
            blanco,
            int(ancho_pantalla / 2 - 150),
            int(largo_pantalla / 2 + 50),
        )
        dibujar_texto(
            str(cuenta_atras),
            fuente40,
            blanco,
            int(ancho_pantalla / 2 - 10),
            int(largo_pantalla / 2 + 100),
        )
        temporizador = pygame.time.get_ticks()
        if temporizador - cuenta_final > 1000:
            cuenta_atras -= 1
            cuenta_final = temporizador


    for event in pygame.event.get():  # llamadas a todos los eventos de usuarios
        if event.type == pygame.QUIT:   # Cerrar el juego una vez termina
            inicio = False

    pygame.display.update()

pygame.quit()
