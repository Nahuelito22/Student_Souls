import pygame
import os
from pytmx.util_pygame import load_pygame
from entities.player import Player

# Configuraciones
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
BG_COLOR = (100, 200, 255) # Azul Cielo (se verá si el mapa no cubre todo)

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
        
        # Límites de la cámara
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = max(-(self.height - SCREEN_HEIGHT), y)
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class LevelEntrance:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_rects = []
        self.interaction_zones = {}
        
        self.state = "playing"
        self.next_scene = None
        self.debug_mode = False

        # Cargar el mapa real
        self.setup_map()

    def setup_map(self):
        # Ruta al nuevo mapa exterior
        map_path = os.path.join("game_assets", "maps", "hub_exterior.tmx")
        
        try:
            self.tmx_data = load_pygame(map_path)
            print("✅ Mapa Exterior cargado.")
        except Exception as e:
            print(f"❌ Error cargando hub_exterior.tmx: {e}")
            return

        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight

        # --- LEER OBJETOS (Colisiones e Interacciones) ---
        for layer_name in ["Colisiones", "Interacciones"]:
            try:
                layer = self.tmx_data.get_layer_by_name(layer_name)
                for obj in layer:
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    
                    # 1. Spawn Point
                    if obj.name == "Spawn_Point":
                        continue # Lo usamos más abajo
                    
                    # 2. Puertas (Interacciones)
                    if obj.name == "Puerta_Uni" or obj.name == "Puerta_Mc":
                        self.interaction_zones[obj.name] = rect
                        print(f"🚪 Puerta detectada: {obj.name}")
                    
                    # 3. Paredes / Suelo (Todo lo demás)
                    else:
                        self.obstacle_rects.append(rect)
                        
            except ValueError:
                pass # Si falta alguna capa no pasa nada

        # --- BUSCAR SPAWN ---
        player_pos = (100, 100) # Default por si falla
        try:
            spawn = self.tmx_data.get_object_by_name("Spawn_Point")
            player_pos = (spawn.x, spawn.y)
        except:
            print("⚠️ Spawn no encontrado en exterior, usando default.")

        # Crear Jugador y Cámara
        self.player = Player(player_pos, [self.all_sprites], self.obstacle_rects)
        self.camera = Camera(self.map_width, self.map_height)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.debug_mode = not self.debug_mode
            
            if event.key == pygame.K_e:
                self.check_interaction()

    def check_interaction(self):
        sensor = self.player.rect.inflate(20, 20)
        for name, rect in self.interaction_zones.items():
            if sensor.colliderect(rect):
                
                if name == "Puerta_Uni":
                    print("🎓 Entrando a la Facultad...")
                    self.next_scene = "Hub" # Cambia a la escena del Hub Interior
                
                elif name == "Puerta_Mc":
                    print("🍔 ¿Hamburguesas? Aún no programado.")

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw(self):
        self.display_surface.fill(BG_COLOR)

        # 1. DIBUJAR MAPA (Capas visibles)
        # Esto dibujará en orden: Cielo, Montañas, Arboles Lejos, Suelo, Edificios, etc.
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        rect = pygame.Rect(x*16, y*16, 16, 16)
                        screen_rect = self.camera.apply_rect(rect)
                        # Optimización: Solo dibujar si entra en pantalla
                        if -32 < screen_rect.x < SCREEN_WIDTH+32 and -32 < screen_rect.y < SCREEN_HEIGHT+32:
                            self.display_surface.blit(tile, screen_rect)

        # 2. DIBUJAR SPRITES (Bob)
        for sprite in self.all_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))

        # 3. INTERFAZ Y DEBUG
        self.draw_ui()
        if self.debug_mode:
            self.draw_debug()

    def draw_ui(self):
        sensor = self.player.rect.inflate(20, 20)
        for name, rect in self.interaction_zones.items():
            if sensor.colliderect(rect):
                msg = ""
                color = (255, 255, 255)
                
                if name == "Puerta_Uni": 
                    msg = "[E] Entrar a la Uni"
                    color = (100, 100, 255)
                elif name == "Puerta_Mc": 
                    msg = "[E] Buscar Trabajo"
                    color = (255, 100, 100)
                
                if msg:
                    font = pygame.font.SysFont("Arial", 14, bold=True)
                    txt = font.render(msg, True, color)
                    bg = txt.get_rect(midbottom=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 40))
                    pygame.draw.rect(self.display_surface, (0,0,0), bg.inflate(10,4))
                    self.display_surface.blit(txt, bg)

    def draw_debug(self):
        for r in self.obstacle_rects:
            pygame.draw.rect(self.display_surface, (255,0,0), self.camera.apply_rect(r), 1)
        for r in self.interaction_zones.values():
            pygame.draw.rect(self.display_surface, (0,255,255), self.camera.apply_rect(r), 2)
        pygame.draw.rect(self.display_surface, (0,255,0), self.camera.apply_rect(self.player.hitbox), 1)