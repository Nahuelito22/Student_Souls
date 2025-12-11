import pygame
import os

# ==============================================================================
# ⚙️ ZONA DE CONFIGURACIÓN VISUAL (¡AQUÍ MUEVES LAS COSAS!)
# ==============================================================================

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

# --- POSICIONES (X, Y) ---
# Usa estos números para mover a los personajes hasta que coincidan con tu imagen.
# (0,0) es arriba a la izquierda. (320, 240) es abajo a la derecha.

# Posición de BOB (Coordenada de los PIES)
# En tu imagen, Bob está abajo a la izquierda.
PLAYER_POS = (70, 190) 

# Posición del ENEMIGO (Coordenada de la BASE)
# En tu imagen, el monstruo está sobre el escritorio del profesor (arriba derecha).
ENEMY_POS = (250, 130)

# --- ESCALA DE IMÁGENES ---
# Si los dibujos se ven muy chicos o grandes, cambia estos multiplicadores.
PLAYER_SCALE = 1.5  # Aumenta a Bob un 50%
ENEMY_SCALE = 1.5   # Aumenta al Monstruo un 50%

# ==============================================================================

class MinigameRPG:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.next_scene = None
        self.font = pygame.font.SysFont("Arial", 16)
        
        # Cargar los gráficos
        self.load_assets()

    def load_assets(self):
        base_path = os.path.join("game_assets", "graphics", "rpg")
        
        try:
            # 1. FONDO (Aula)
            self.bg = pygame.image.load(os.path.join(base_path, "bg_battle.png")).convert()
            self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # 2. BOB (Vista Trasera)
            bob_img = pygame.image.load(os.path.join(base_path, "bob_battle_back.png")).convert_alpha()
            # Escalamos según la configuración
            w, h = bob_img.get_size()
            self.bob_sprite = pygame.transform.scale(bob_img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
            
            # 3. ENEMIGO (El Sistema)
            enemy_img = pygame.image.load(os.path.join(base_path, "enemy_system.png")).convert_alpha()
            w, h = enemy_img.get_size()
            self.enemy_sprite = pygame.transform.scale(enemy_img, (int(w * ENEMY_SCALE), int(h * ENEMY_SCALE)))
            
        except Exception as e:
            print(f"❌ Error cargando assets RPG: {e}")
            # Fallbacks (Cuadros de colores por si falla)
            self.bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.bg.fill((20, 20, 40))
            self.bob_sprite = pygame.Surface((32, 32)); self.bob_sprite.fill((0, 0, 255))
            self.enemy_sprite = pygame.Surface((64, 64)); self.enemy_sprite.fill((255, 0, 0))

        # --- CREAR RECTÁNGULOS (Para posicionar) ---
        # Usamos 'midbottom' para que las coordenadas (X,Y) representen los PIES del personaje
        self.bob_rect = self.bob_sprite.get_rect(midbottom=PLAYER_POS)
        self.enemy_rect = self.enemy_sprite.get_rect(midbottom=ENEMY_POS)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Salir con ESC (vuelve al Hub)
            if event.key == pygame.K_ESCAPE:
                self.next_scene = "Hub"

    def update(self):
        # Aquí irá la lógica de turnos después
        pass

    def draw(self):
        # 1. Dibujar Fondo
        self.display_surface.blit(self.bg, (0, 0))
        
        # 2. Dibujar Entidades
        self.display_surface.blit(self.bob_sprite, self.bob_rect)
        self.display_surface.blit(self.enemy_sprite, self.enemy_rect)
        
        # 3. UI PROVISORIA (Panel de Texto)
        # Dibujamos un rectángulo negro abajo para el menú
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.display_surface, (0, 0, 0), panel_rect)
        pygame.draw.rect(self.display_surface, (255, 255, 255), panel_rect, 2) # Borde blanco
        
        text = self.font.render("¡Apareció EL SISTEMA salvaje!", True, (255, 255, 255))
        self.display_surface.blit(text, (20, SCREEN_HEIGHT - 45))