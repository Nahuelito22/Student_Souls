import pygame
import asyncio
import os
from pytmx.util_pygame import load_pygame
from entities.player import Player
from pygame import Rect

# --- CONFIGURACIÓN ---
SCREEN_WIDTH = 320   
SCREEN_HEIGHT = 240
SCALE_FACTOR = 3    
FPS = 60
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

class Game:
    def __init__(self):
        pygame.init()
        self.screen_window = pygame.display.set_mode((SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
        self.screen_native = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Student Souls: Hub Central")
        self.clock = pygame.time.Clock()
        self.running = True

        self.all_sprites = pygame.sprite.Group()
        self.obstacle_rects = [] # Lista para guardar paredes

        # --- CARGAR MAPA ---
        map_path = os.path.join("game_assets", "maps", "hub_interior.tmx")
        try:
            self.tmx_data = load_pygame(map_path)
            print("✅ Mapa cargado.")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.running = False
            return

        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight
        
        # --- CARGAR PAREDES (COLLISIONS) ---
        # Buscamos la capa de objetos llamada 'Colisiones'
        try:
            collision_layer = self.tmx_data.get_layer_by_name("Colisiones")
            for obj in collision_layer:
                # Si el objeto tiene nombre "Spawn_Point", NO es pared
                if obj.name == "Spawn_Point":
                    continue
                
                # Creamos un Rect de pygame para cada pared
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.obstacle_rects.append(rect)
                
            print(f"🧱 Paredes cargadas: {len(self.obstacle_rects)}")
        except ValueError:
            print("⚠️ AVISO: No se encontró capa 'Colisiones'")

        # --- BUSCAR SPAWN ---
        player_pos = (100, 100)
        try:
            spawn_obj = self.tmx_data.get_object_by_name("Spawn_Point")
            player_pos = (spawn_obj.x, spawn_obj.y)
        except:
            pass

        # Crear Jugador (Le pasamos las paredes)
        self.player = Player(player_pos, [self.all_sprites], self.obstacle_rects)
        self.camera = Camera(self.map_width, self.map_height)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw_map(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        world_x = x * self.tmx_data.tilewidth
                        world_y = y * self.tmx_data.tileheight
                        
                        rect = pygame.Rect(world_x, world_y, self.tmx_data.tilewidth, self.tmx_data.tileheight)
                        screen_rect = self.camera.apply_rect(rect)
                        
                        if -32 < screen_rect.x < SCREEN_WIDTH + 32 and -32 < screen_rect.y < SCREEN_HEIGHT + 32:
                            self.screen_native.blit(tile, screen_rect)

    def draw(self):
        self.screen_native.fill(BG_COLOR)

        if self.running:
            self.draw_map()
        
        # DEBUG: Si quieres ver las paredes rojas para comprobar si funcionan
        # for wall in self.obstacle_rects:
        #    pygame.draw.rect(self.screen_native, (255, 0, 0), self.camera.apply_rect(wall), 1)

        for sprite in self.all_sprites:
            self.screen_native.blit(sprite.image, self.camera.apply(sprite))

        frame_scaled = pygame.transform.scale(self.screen_native, (SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
        self.screen_window.blit(frame_scaled, (0, 0))
        pygame.display.flip()

    async def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(0)

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())