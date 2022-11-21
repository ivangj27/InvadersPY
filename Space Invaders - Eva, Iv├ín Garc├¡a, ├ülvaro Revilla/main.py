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
clock = pygame.time.Clock()
fps = 60

# Creación de ventana (Tamaño, titulo):
screen_width = 600
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))  # display surface
pygame.display.set_caption("Space Invanders")  # Nombre ventana

# Definimos variables de fuentes
#                        (Path/Nombre fuente, tamaño)
font30 = pygame.font.Font("Fuentes/Goldman-Regular.ttf", 30)
font40 = pygame.font.Font("Fuentes/Goldman-Regular.ttf", 40)

# Carga de ficheros de sonido de explosión y de disparo del juego
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)
explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)
laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

# Definición de columnas y filas del array de aliens
rows = 5
cols = 5
alien_cooldown = 1000  # Tiempo de enfriamiento entre disparos de los alienígenas
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0  # 0 es estado neutro, 1 para cuando el jugador ha ganado, -1 para cuando el jugador ha perdido

# Colores a utilizar
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# Carga de imagen de fondo
bg = pygame.image.load("img/bg.png")


def draw_bg():
    screen.blit(bg, (0, 0))


# Función de creación del texto en pantalla
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col,'black')
    screen.blit(img, (x, y))


# Creación de la clase de la nave del jugador
class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # Velocidad de movimiento base del jugador
        speed = 8
        # Tiempo de enfriamiento entre disparos del jugador en milisegundos
        cooldown = 500
        game_over = 0

        # Controles de movimiento del jugador
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        time_now = pygame.time.get_ticks()
        # Control de disparo del jugador
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        self.mask = pygame.mask.from_surface(self.image)

        # Barra de vida
        pygame.draw.rect(
            screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15)
        )
        if self.health_remaining > 0:
            pygame.draw.rect(
                screen,
                green,
                (
                    self.rect.x,
                    (self.rect.bottom + 10),
                    int(self.rect.width * (self.health_remaining / self.health_start)),
                    15,
                ),
            )

        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over=-1
            
   
        if pygame.sprite.spritecollide(
                self, alien_group, False, pygame.sprite.collide_mask
        ):
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
            
        return game_over


# Creación de la clase que define los disparos
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


# Creación de clase para los aliens
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien1.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_direction_x = 1

    def update(self):
        self.rect.x += self.move_direction_x
        if self.rect.x + self.rect.width > screen_width - self.rect.width or self.rect.x < 0:
                self.move_direction_x *= -1
                self.rect.y += 50

        
      


# Creación de las balas de los aliens
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(
                self, spaceship_group, False, pygame.sprite.collide_mask
        ):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            spaceship.health_remaining -= 1
            spaceship.health_visibility = True
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


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
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # Actualizar la animación de la explosión
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # Si la animacion ha terminado borrar la explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


# Grupos de sprites
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


# Función para generar los alienígenas en las filas y columnas definidas
def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70)
            alien_group.add(alien)


create_aliens()

# Creación del jugador
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

# Bucle principal del juego donde ejecutaremos las funciones:
run = True
while run:

    clock.tick(fps)

    # Se dibuja el fondo
    draw_bg()
    draw_text(
        "SPACE INVADERS",
        font40,
        white,
        int(screen_width / 2 - 185),
        int(20),
    )
    
    # Actualización de las explosiones
    explosion_group.update()

    # Se dibujan los grupos de sprites en pantalla
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    
    if countdown == 0:
        # Se crean aleatoriamente los disparos de los aliens
        time_now = pygame.time.get_ticks()
        if (
                time_now - last_alien_shot > alien_cooldown
                and len(alien_bullet_group) < 5
                and len(alien_group) > 0
        ):
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(
                attacking_alien.rect.centerx, attacking_alien.rect.bottom
            )
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now

        # Comprobación de condición de victoria
        if len(alien_group) == 0:
            game_over = 1

        if game_over == 0:
            # Actualización del jugador en pantalla
            game_over = spaceship.update()

            # Actualización de los sprites
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()

        else:
            if game_over == -1:
                draw_text(
                    "HAS PERDIDO!",
                    font40,
                    white,
                    int(screen_width / 2 - 150),
                    int(screen_height / 2 + 50),
                )
                
            if game_over == 1:
                draw_text(
                    "HAS GANADO!",
                    font40,
                    white,
                    int(screen_width / 2 - 150),
                    int(screen_height / 2 + 50),
                )
            

    if countdown > 0:
        draw_text(
            "PREPÁRATE!",
            font40,
            white,
            int(screen_width / 2 - 150),
            int(screen_height / 2 + 50),
        )
        draw_text(
            str(countdown),
            font40,
            white,
            int(screen_width / 2 - 10),
            int(screen_height / 2 + 100),
        )
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    for event in pygame.event.get():  # llamadas a todos los eventos de usuarios
        if event.type == pygame.QUIT:   # Cerrar el juego una vez termina
            run = False

    pygame.display.update()

pygame.quit()
