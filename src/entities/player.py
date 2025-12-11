import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups) # Inicializa la clase padre (Sprite)
        
        # 1. Cargar la imagen (Sprite)
        # Usamos os.path.join para que funcione en Windows/Mac/Linux
        image_path = os.path.join("game_assets", "graphics", "player", "Bob_idle_16x16.png")
        
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print("⚠️ Error: No encuentro a Bob. Creando un cuadrado rojo de repuesto.")
            self.image = pygame.Surface((16, 16))
            self.image.fill('red')

        # 2. Definir la posición (Hitbox / Rect)
        self.rect = self.image.get_rect(topleft=pos)
        
        # 3. Movimiento (Vectores)
        self.direction = pygame.math.Vector2() # Vector (x, y) que será 0, 1 o -1
        self.speed = 2 # Velocidad de movimiento (píxeles por frame)

    def input(self):
        """Detecta qué teclas está pulsando el usuario"""
        keys = pygame.key.get_pressed()

        # Movimiento Vertical (W / S o Flechas)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # Movimiento Horizontal (A / D o Flechas)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self, speed):
        """Aplica el movimiento al rectángulo"""
        # Normalizar vector (para que no corra más rápido en diagonal)
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Mover en X
        self.rect.x += self.direction.x * speed
        # Mover en Y
        self.rect.y += self.direction.y * speed

    def update(self):
        """El cerebro de Bob: se ejecuta 60 veces por segundo"""
        self.input()
        self.move(self.speed)