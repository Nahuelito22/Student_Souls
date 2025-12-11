import pygame
import os
from pytmx.util_pygame import load_pygame
from entities.player import Player

# --- CONFIGURACIÓN COPIADA DEL MAIN ---
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
BG_COLOR = (20, 20, 20)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = max(-(self.height - SCREEN_HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)

class LevelHub:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        
        self.state = "playing"
        self.dialog_text = []
        self.debug_mode = False

        self.all_sprites = pygame.sprite.Group()
        self.obstacle_rects = []
        self.interaction_zones = {}

        # --- CARGAR MAPA (Lógica exacta de tu main) ---
        map_path = os.path.join("game_assets", "maps", "hub_interior.tmx")
        try:
            self.tmx_data = load_pygame(map_path)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return

        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight

        # --- 1. CARGAR PAREDES (Capa 'Colisiones') ---
        # Tu lógica original: Todo lo que NO sea Spawn ni Aula es pared.
        # Esto hace que "Tutorial_Zone" sea pared automáticamente porque no se filtra.
        try:
            collision_layer = self.tmx_data.get_layer_by_name("Colisiones")
            for obj in collision_layer:
                if obj.name == "Spawn_Point" or (obj.name and "Aula" in obj.name):
                    continue
                
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.obstacle_rects.append(rect)
        except ValueError:
            pass

        # --- 2. CARGAR INTERACCIONES ---
        # Tu lógica original buscaba en ambas capas
        self.cargar_interactivos("Interacciones")
        self.cargar_interactivos("Colisiones")

        # --- SPAWN ---
        player_pos = (100, 100)
        try:
            spawn_obj = self.tmx_data.get_object_by_name("Spawn_Point")
            player_pos = (spawn_obj.x, spawn_obj.y)
        except:
            pass

        # Crear Jugador y Cámara
        self.player = Player(player_pos, [self.all_sprites], self.obstacle_rects)
        self.camera = Camera(self.map_width, self.map_height)

    def cargar_interactivos(self, layer_name):
        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
            for obj in layer:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                
                # Detectar Aulas
                if obj.name and "Aula" in obj.name:
                    self.interaction_zones[obj.name] = rect
                
                # Detectar Tutorial
                elif obj.name == "Tutorial_Zone":
                    self.interaction_zones[obj.name] = rect
        except ValueError:
            pass

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.debug_mode = not self.debug_mode
            
            if event.key == pygame.K_ESCAPE:
                return True
            
            if event.key == pygame.K_e:
                if self.state == "playing":
                    self.check_interaction()
                elif self.state == "dialogue":
                    self.state = "playing"

    def check_interaction(self):
        bob_sensor = self.player.rect.inflate(20, 20)
        for name, zone_rect in self.interaction_zones.items():
            if bob_sensor.colliderect(zone_rect):
                
                # TU TEXTO ORIGINAL COMPLETO
                if name == "Tutorial_Zone":
                    self.state = "dialogue"
                    self.dialog_text = [
                        "Bienvenido a Student Souls.",
                        "Usa las FLECHAS para moverte.",
                        "Acércate a las puertas y presiona E para rendir.",
                        "Cuidado: Si tu dinero o cordura bajan a 0...",
                        "¡Pierdes la regularidad!"
                    ]
                
                elif name == "Aula_Runner":
                    print("🚀 ¡Iniciando Cursada Infinita!")
                    self.next_scene = "Runner"
                elif name == "Aula_RPG":
                    print("⚔️ Entrando al combate...")
                    self.next_scene = "RPG" # <--- ESTO ES LO NUEVO
                elif name == "Aula_TP":
                    print("--> HACER EL TP")
                elif name == "Aula_Admin":
                    print("--> BUROCRACIA")

    def update(self):
        if self.state == "playing":
            self.all_sprites.update()
            self.camera.update(self.player)

    def draw(self):
        self.display_surface.fill(BG_COLOR)

        # Dibujar Mapa (Copiado de tu main)
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        world_x = x * self.tmx_data.tilewidth
                        world_y = y * self.tmx_data.tileheight
                        rect = pygame.Rect(world_x, world_y, self.tmx_data.tilewidth, self.tmx_data.tileheight)
                        screen_rect = self.camera.apply_rect(rect)
                        
                        # Optimización visual
                        if -32 < screen_rect.x < SCREEN_WIDTH + 32 and -32 < screen_rect.y < SCREEN_HEIGHT + 32:
                            self.display_surface.blit(tile, screen_rect)

        # Dibujar Sprites
        for sprite in self.all_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))

        self.draw_ui()
        self.draw_dialog()
        
        if self.debug_mode:
            self.draw_debug()

    def draw_ui(self):
        bob_sensor = self.player.rect.inflate(20, 20)
        for name, zone_rect in self.interaction_zones.items():
            if bob_sensor.colliderect(zone_rect):
                font = pygame.font.SysFont("Arial", 14, bold=True)
                msg = ""
                color = (255, 255, 255)

                if name == "Aula_Runner":
                    msg = "[E] Cursada Infinita"
                    color = (100, 255, 100)
                elif name == "Aula_RPG":
                    msg = "[E] Final: El Sistema"
                    color = (255, 100, 100)
                elif name == "Aula_TP":
                    msg = "[E] TP Grupal"
                    color = (100, 100, 255)
                elif name == "Aula_Admin":
                    msg = "[E] Inscripción"
                    color = (255, 255, 0)
                elif name == "Tutorial_Zone":
                    msg = "[E] Pagar Matrícula (Tutorial)" 
                    color = (255, 255, 255)

                if msg:
                    text_surf = font.render(msg, True, color)
                    bg_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 20))
                    pygame.draw.rect(self.display_surface, (0,0,0), bg_rect.inflate(10, 4))
                    self.display_surface.blit(text_surf, bg_rect)

    def draw_dialog(self):
        if self.state == "dialogue":
            margin = 20
            height = 90
            rect = pygame.Rect(margin, SCREEN_HEIGHT - height - margin, SCREEN_WIDTH - (margin*2), height)
            
            pygame.draw.rect(self.display_surface, (0, 0, 150), rect)
            pygame.draw.rect(self.display_surface, (255, 255, 255), rect, 2)
            
            font = pygame.font.SysFont("Arial", 12)
            y_offset = 10
            
            for line in self.dialog_text:
                text_surf = font.render(line, True, (255, 255, 255))
                self.display_surface.blit(text_surf, (rect.x + 10, rect.y + y_offset))
                y_offset += 15
                
            press_e = font.render("[E] Cerrar", True, (255, 255, 0))
            self.display_surface.blit(press_e, (rect.right - 60, rect.bottom - 15))

    def draw_debug(self):
        for wall in self.obstacle_rects:
            pygame.draw.rect(self.display_surface, (255, 0, 0), self.camera.apply_rect(wall), 1)
        pygame.draw.rect(self.display_surface, (0, 255, 0), self.camera.apply_rect(self.player.hitbox), 1)