import pygame
import random

# --- CONFIGURACIÓN DEL MINIJUEGO ---
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
BG_COLOR = (135, 206, 235) # Un azul cielo diferente para distinguir
GROUND_HEIGHT = 40
SCROLL_SPEED = 4 # Qué tan rápido se mueve el mundo hacia la izquierda

class RunnerPlayer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Placeholder: Un cuadrado azul para Bob de perfil
        self.image = pygame.Surface((16, 32))
        self.image.fill((50, 50, 255))
        self.rect = self.image.get_rect()
        
        # Posición inicial (Izquierda, sobre el suelo)
        self.rect.x = 40
        self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
        
        # FÍSICA DE SALTO
        self.gravity = 0.8
        self.jump_power = -12
        self.velocity_y = 0
        self.is_jumping = False

    def update(self):
        # Aplicar gravedad
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Colisión con el suelo (simple)
        floor_y = SCREEN_HEIGHT - GROUND_HEIGHT
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
            self.velocity_y = 0
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            print("🦘 ¡Salto!")

class MinigameRunner:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.state = "playing"
        self.next_scene = None # Para volver al Hub si pierde/gana

        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        
        # Crear Jugador
        self.player = RunnerPlayer()
        self.all_sprites.add(self.player)

        # Variables del entorno
        self.ground_x = 0
        self.score = 0
        font_path = pygame.font.match_font('arial')
        self.font = pygame.font.Font(font_path, 16)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Salto con ESPACIO o FLECHA ARRIBA
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                self.player.jump()
            
            # Tecla de debug para salir rápido
            if event.key == pygame.K_q:
                print("🔙 Volviendo al Hub...")
                self.next_scene = "Hub"

    def update(self):
        if self.state == "playing":
            # 1. Mover el suelo (Scrolling)
            self.ground_x -= SCROLL_SPEED
            # Si una baldosa de suelo sale por completo, la reiniciamos
            if self.ground_x <= -SCREEN_WIDTH:
                self.ground_x = 0
            
            # 2. Actualizar físicas del jugador
            self.all_sprites.update()
            
            # 3. Aumentar puntaje (distancia recorrida)
            self.score += 1

    def draw(self):
        self.display_surface.fill(BG_COLOR)

        # 1. DIBUJAR SUELO INFINITO (Dos rectángulos que se persiguen)
        # Suelo 1 (El que está en pantalla)
        pygame.draw.rect(self.display_surface, (100, 60, 20), (self.ground_x, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        # Suelo 2 (El que viene entrando por la derecha)
        pygame.draw.rect(self.display_surface, (100, 60, 20), (self.ground_x + SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        # 2. Sprites
        self.all_sprites.draw(self.display_surface)
        
        # 3. UI (Puntaje)
        score_surf = self.font.render(f"Distancia: {self.score // 10}m", True, (0,0,0))
        self.display_surface.blit(score_surf, (10, 10))