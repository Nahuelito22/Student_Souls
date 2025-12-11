import pygame
import asyncio
from pytmx.util_pygame import load_pygame
import os

# ### NUEVO: Importar la clase Player
from entities.player import Player 

# --- CONSTANTES ---
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
SCALE_FACTOR = 3
FPS = 60

# --- COLORES ---
BLACK = (0, 0, 0)
BG_COLOR = (20, 20, 20)

class Game:
    def __init__(self):
        pygame.init()
        self.screen_native = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_scaled = pygame.display.set_mode((SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
        pygame.display.set_caption("Student Souls: Veintipico Edition")
        self.clock = pygame.time.Clock()
        self.running = True

        # ### NUEVO: Grupo de Sprites (Aquí guardaremos a Bob y otros personajes)
        self.all_sprites = pygame.sprite.Group()

        # Cargar Mapa
        map_path = os.path.join("game_assets", "maps", "hub_interior.tmx")
        try:
            self.tmx_data = load_pygame(map_path)
            print(f"✅ Mapa cargado: {map_path}")
        except FileNotFoundError:
            print(f"❌ ERROR: No encuentro el mapa en {map_path}")
            self.running = False
            return # Salir si falla

        # ### NUEVO: Buscar el Spawn Point y Crear a Bob
        player_spawn_pos = (100, 100) # Posición por defecto por si fallamos en Tiled
        
        # Buscamos en la capa de objetos 'Colisiones' (o como la hayas llamado)
        obj_layer = self.tmx_data.get_layer_by_name("Colisiones")
        for obj in obj_layer:
            if obj.name == "Spawn_Point": # Tiene que coincidir con el nombre que pusiste en Tiled
                player_spawn_pos = (obj.x, obj.y)
                print(f"📍 Spawn encontrado en: {player_spawn_pos}")
                break
        
        # Instanciamos a Bob
        self.player = Player(player_spawn_pos, [self.all_sprites])


    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def draw_map(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.screen_native.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

    def update(self):
        # ### NUEVO: Actualizar todos los sprites (mueve a Bob)
        self.all_sprites.update()

    def draw(self):
        self.screen_native.fill(BG_COLOR)

        # 1. Dibujar Mapa
        if self.running:
            self.draw_map()
        
        # ### NUEVO: Dibujar Sprites (Dibuja a Bob encima del mapa)
        self.all_sprites.draw(self.screen_native)

        # Escalar y mostrar
        frame = pygame.transform.scale(self.screen_native, (SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
        self.screen_scaled.blit(frame, (0, 0))
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