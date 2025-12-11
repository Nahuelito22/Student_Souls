import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        
        # Configuración
        self.width = 16
        self.height = 32
        
        # Guardamos las paredes para chequear colisiones luego
        self.obstacle_sprites = obstacle_sprites 

        # 1. Cargar animaciones
        self.import_assets()
        
        # Estado inicial
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15
        
        # Imagen
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Hitbox: Es un rect más pequeño (solo los pies) para colisiones precisas
        # inflate(-X, -Y) reduce el tamaño. 
        # Reducimos ancho un poco y altura a la mitad (solo pies)
        self.hitbox = self.rect.inflate(-4, -16) 

        # Movimiento
        self.direction = pygame.math.Vector2()
        self.speed = 2

    def import_assets(self):
        path = os.path.join("game_assets", "graphics", "player")
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': []}

        # IDLE
        idle_path = os.path.join(path, "Bob_idle_16x16.png")
        try:
            idle_sheet = pygame.image.load(idle_path).convert_alpha()
            self.animations['right_idle'].append(self.get_image(idle_sheet, 0, 0))
            self.animations['up_idle'].append(self.get_image(idle_sheet, 16, 0))
            self.animations['left_idle'].append(self.get_image(idle_sheet, 32, 0))
            self.animations['down_idle'].append(self.get_image(idle_sheet, 48, 0))
        except:
            print("⚠️ Error cargando Idle")

        # RUN
        run_path = os.path.join(path, "Bob_run_16x16.png")
        try:
            run_sheet = pygame.image.load(run_path).convert_alpha()
            for i in range(6): self.animations['right'].append(self.get_image(run_sheet, i*16, 0))
            for i in range(6): self.animations['up'].append(self.get_image(run_sheet, (i+6)*16, 0))
            for i in range(6): self.animations['left'].append(self.get_image(run_sheet, (i+12)*16, 0))
            for i in range(6): self.animations['down'].append(self.get_image(run_sheet, (i+18)*16, 0))
        except:
             print("⚠️ Error cargando Run. Usando Idle.")
             self.animations['right'] = self.animations['right_idle']
             self.animations['up'] = self.animations['up_idle']
             self.animations['left'] = self.animations['left_idle']
             self.animations['down'] = self.animations['down_idle']

    def get_image(self, sheet, x, y):
        image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), (x, y, self.width, self.height))
        return image

    def input(self):
        keys = pygame.key.get_pressed()
        
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

    def move(self, speed):
        # Normalizar velocidad diagonal
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # --- EJE X ---
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')

        # --- EJE Y ---
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        # Actualizar el rect visual basado en la hitbox (que es la física)
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        # Recorremos todas las paredes (rectángulos) que pasamos desde el Main
        for wall in self.obstacle_sprites:
            if self.hitbox.colliderect(wall):
                if direction == 'horizontal':
                    if self.direction.x > 0: # Yendo a la derecha
                        self.hitbox.right = wall.left
                    if self.direction.x < 0: # Yendo a la izquierda
                        self.hitbox.left = wall.right
                
                if direction == 'vertical':
                    if self.direction.y > 0: # Yendo abajo
                        self.hitbox.bottom = wall.top
                    if self.direction.y < 0: # Yendo arriba
                        self.hitbox.top = wall.bottom

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status:
                self.status = self.status + '_idle'

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]

    def update(self):
        self.input()
        self.get_status()
        self.animate()
        self.move(self.speed)