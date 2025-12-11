import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        
        # Configuración de dimensiones
        self.width = 16
        self.height = 32
        
        # 1. Cargar todas las animaciones (Idle y Run)
        self.import_assets()
        
        # Estado inicial
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15 # Velocidad de animación
        
        # Imagen inicial
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Movimiento
        self.direction = pygame.math.Vector2()
        self.speed = 2

    def import_assets(self):
        """Carga y recorta las hojas de sprites"""
        path = os.path.join("game_assets", "graphics", "player")
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': []}

        # --- CARGAR IDLE (64x32) ---
        # Orden: Derecha(0), Arriba(1), Izquierda(2), Abajo(3) - 1 Frame cada uno
        idle_path = os.path.join(path, "Bob_idle_16x16.png")
        idle_sheet = pygame.image.load(idle_path).convert_alpha()
        
        self.animations['right_idle'].append(self.get_image(idle_sheet, 0, 0))
        self.animations['up_idle'].append(self.get_image(idle_sheet, 16, 0))
        self.animations['left_idle'].append(self.get_image(idle_sheet, 32, 0))
        self.animations['down_idle'].append(self.get_image(idle_sheet, 48, 0))

        # --- CARGAR RUN (384x32) ---
        # Tira larga con 24 frames en total (6 por dirección)
        # Orden asumido: Derecha -> Arriba -> Izquierda -> Abajo
        run_path = os.path.join(path, "Bob_run_16x16.png")
        
        try:
            run_sheet = pygame.image.load(run_path).convert_alpha()
            
            # Recortamos los 24 frames
            for i in range(6): self.animations['right'].append(self.get_image(run_sheet, i*16, 0))       # 0-5
            for i in range(6): self.animations['up'].append(self.get_image(run_sheet, (i+6)*16, 0))      # 6-11
            for i in range(6): self.animations['left'].append(self.get_image(run_sheet, (i+12)*16, 0))   # 12-17
            for i in range(6): self.animations['down'].append(self.get_image(run_sheet, (i+18)*16, 0))   # 18-23
            
        except FileNotFoundError:
            print("⚠️ ERROR: No se encontró Bob_run_16x16.png. Usando Idle como respaldo.")
            # Si falla, usamos los idle para correr también
            self.animations['right'] = self.animations['right_idle']
            self.animations['up'] = self.animations['up_idle']
            self.animations['left'] = self.animations['left_idle']
            self.animations['down'] = self.animations['down_idle']

    def get_image(self, sheet, x, y):
        """Herramienta de recorte"""
        image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), (x, y, self.width, self.height))
        return image

    def input(self):
        keys = pygame.key.get_pressed()
        
        # Movimiento
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

    def get_status(self):
        # Si el jugador no se mueve, agregamos "_idle" al estado
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status:
                self.status = self.status + '_idle'

    def animate(self):
        # Buscamos la lista de imágenes correcta según el estado (ej: 'down' o 'down_idle')
        animation = self.animations[self.status]

        # Avanzamos el frame
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Actualizamos la imagen
        self.image = animation[int(self.frame_index)]

    def update(self):
        self.input()
        self.get_status() # Calcula si está quieto o corriendo
        self.animate()    # Elige el dibujo correcto
        
        # Mover y normalizar
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed