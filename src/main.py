import pygame
import sys
import os
from pytmx.util_pygame import load_pygame

# Importamos a Bob (Asegúrate de que player.py esté en la carpeta entities)
from entities.player import Player 

# --- CONFIGURACIÓN ---
SCREEN_WIDTH = 320   # Resolución nativa (pequeña)
SCREEN_HEIGHT = 240
SCALE_FACTOR = 3     # Escalado x3
FPS = 60

# Colores
BG_COLOR = (20, 20, 20)

class Game:
    def __init__(self):
        pygame.init()
        # Pantalla real (escalada)
        self.screen_window = pygame.display.set_mode((SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
        # Lienzo pequeño donde dibujamos pixel art
        self.screen_native = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Student Souls: Hub Central")
        self.clock = pygame.time.Clock()
        self.running = True

        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()

        # --- CARGAR MAPA (TMX) ---
        # Ajusta esta ruta si tu tmx está en otro lado
        map_path = os.path.join("game_assets", "maps", "hub_interior.tmx")
        
        try:
            # load_pygame se encarga de cargar las imagenes y datos
            self.tmx_data = load_pygame(map_path)
            print("✅ Mapa cargado correctamente.")
        except Exception as e:
            print(f"❌ ERROR CRÍTICO: No se pudo cargar el mapa.\n{e}")
            self.running = False
            return

        # --- BUSCAR SPAWN POINT ---
        # Buscamos en la capa de objetos "Colisiones"
        player_pos = (100, 100) # Posición de respaldo
        
        try:
            # Buscamos el objeto por nombre
            spawn_obj = self.tmx_data.get_object_by_name("Spawn_Point")
            player_pos = (spawn_obj.x, spawn_obj.y)
            print(f"📍 Spawn encontrado en: {player_pos}")
        except:
            print("⚠️ AVISO: No se encontró un objeto llamado 'Spawn_Point' en Tiled. Usando (100,100).")

        # --- CREAR A BOB ---
        self.player = Player(player_pos, [self.all_sprites])

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        self.all_sprites.update()

    def draw_map(self):
        # Dibujamos capa por capa
        for layer in self.tmx_data.visible_layers:
            # Si es una capa de tiles (Suelo, Paredes, Decoracion)
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        # Dibujamos el tile en su posición
                        self.screen_native.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))
            
            # (Opcional) Si quieres ver los objetos de colisión para depurar
            # elif isinstance(layer, pytmx.TiledObjectGroup):
            #     for obj in layer:
            #         rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            #         pygame.draw.rect(self.screen_native, (255, 0, 0), rect, 1)

    def draw(self):
        self.screen_native.fill(BG_COLOR)

        # 1. Dibujar el Mapa (Fondo)
        if self.running:
            self.draw_map()

        # 2. Dibujar a Bob (y otros sprites)
        # Nota: Si quieres que Bob pase "detrás" de las mesas, 
        # hay que dibujar el mapa en capas separadas (Suelo abajo, Bob en medio, Decoración arriba)
        # Por ahora lo dibujamos encima de todo.
        self.all_sprites.draw(self.screen_native)

        # 3. Escalar y mostrar en ventana grande
        frame_scaled = pygame.transform.scale(self.screen_native, (SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
        self.screen_window.blit(frame_scaled, (0, 0))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()