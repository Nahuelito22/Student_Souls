import pygame
import os

class Player(pygame.sprite.Sprite):
    
    def __init__(self, pos, groups):
        super().__init__(groups)
        
        # Ruta a tu imagen
        image_path = os.path.join("game_assets", "graphics", "player", "Bob_idle_16x16.png")
        
        try:
            # 1. Cargamos la hoja completa (64x32 px)
            self.full_sheet = pygame.image.load(image_path).convert_alpha()
            
            # Dimensiones de CADA cuadro individual de Bob
            self.width = 16
            self.height = 32
            
            # 2. Diccionario de Animaciones (RECORTES HORIZONTALES)
            # Tu imagen tiene este orden: Derecha -> Arriba -> Izquierda -> Abajo
            # Y todos están en la fila 0 (y=0)
            
            self.animations = {
                'right': self.get_image(0, 0),        # x=0  (Primer Bob)
                'up':    self.get_image(16, 0),       # x=16 (Segundo Bob)
                'left':  self.get_image(32, 0),       # x=32 (Tercer Bob)
                'down':  self.get_image(48, 0)        # x=48 (Cuarto Bob)
            }
            
        except FileNotFoundError:
            print("⚠️ Error: No encuentro a Bob.")
            # Fallback: cuadrado rojo si falla la carga
            self.full_sheet = None
            self.animations = {
                'down': pygame.Surface((16, 32)),
                'up': pygame.Surface((16, 32)),
                'left': pygame.Surface((16, 32)),
                'right': pygame.Surface((16, 32))
            }
            for key in self.animations: self.animations[key].fill('red')

        # Estado inicial
        self.status = 'down' # Empieza mirando al frente (Abajo)
        self.image = self.animations[self.status]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Movimiento
        self.direction = pygame.math.Vector2()
        self.speed = 2

    def get_image(self, x, y):
        """Herramienta para recortar un pedazo de la hoja grande"""
        # Crea un lienzo transparente del tamaño de UN solo Bob
        image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Pega el pedazo que queremos (desde x, y del sheet original)
        image.blit(self.full_sheet, (0, 0), (x, y, self.width, self.height))
        return image

    def input(self):
        keys = pygame.key.get_pressed()

        # Reseteamos dirección para que pare si no tocas nada
        self.direction.x = 0
        self.direction.y = 0

        # --- EJE VERTICAL (Arriba / Abajo) ---
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'

        # --- EJE HORIZONTAL (Izquierda / Derecha) ---
        # El eje horizontal sobrescribe el estado para que se vea de lado al ir en diagonal
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'

    def move(self, speed):
        # Normalizar vector para que no corra más rápido en diagonal
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * speed
        self.rect.y += self.direction.y * speed

    def update(self):
        # 1. Leer teclado
        self.input()
        # 2. Mover rectángulo
        self.move(self.speed)
        # 3. ACTUALIZAR IMAGEN: Cambia la foto según a dónde mire
        self.image = self.animations[self.status]