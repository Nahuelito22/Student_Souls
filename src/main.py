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
        
        # DEBUG MODE (Actívalo con F1)
        self.debug_mode = False 

        self.state = "playing" # Puede ser "playing" o "dialogue"
        self.dialog_text = []  # Lista de líneas de texto a mostrar

        self.all_sprites = pygame.sprite.Group()
        self.obstacle_rects = []    # Lista de Paredes (Sólidas)
        self.interaction_zones = {} # Diccionario de Puertas/Zonas (Interactuables)

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
        
        # --- 1. CARGAR PAREDES (Capa 'Colisiones') ---
        try:
            collision_layer = self.tmx_data.get_layer_by_name("Colisiones")
            for obj in collision_layer:
                # Ignoramos Spawn y Zonas si quedaron ahí por error
                if obj.name == "Spawn_Point" or (obj.name and "Aula" in obj.name):
                    continue
                
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.obstacle_rects.append(rect)
            print(f"🧱 Paredes cargadas: {len(self.obstacle_rects)}")
        except ValueError:
            print("⚠️ AVISO: No se encontró capa 'Colisiones'")

        # --- 2. CARGAR PUERTAS (Capa 'Interacciones') ---
        try:
            interaction_layer = self.tmx_data.get_layer_by_name("Interacciones")
            for obj in interaction_layer:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                
                # Guardamos la zona con su nombre (ej: "Aula_Runner")
                if obj.name:
                    self.interaction_zones[obj.name] = rect
                    print(f"🚪 Zona cargada: {obj.name}")
                    
        except ValueError:
            print("⚠️ AVISO: No se encontró capa 'Interacciones'")

        # --- 2. CARGAR PUERTAS Y ZONAS ---
        try:
            interaction_layer = self.tmx_data.get_layer_by_name("Colisiones") # Ojo: Revisa si lo pusiste en Colisiones o Interacciones
            # Según tu último TMX, Tutorial_Zone estaba en 'Colisiones' (ID 5)
            # Y las Aulas en 'Interacciones'. Vamos a leer AMBAS capas buscando interacciones.
            
            # Función auxiliar para leer objetos interactivos
            def cargar_interactivos(capa):
                for obj in capa:
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    
                    # Detectar Aulas
                    if obj.name and "Aula" in obj.name:
                        self.interaction_zones[obj.name] = rect
                    
                    # Detectar Tutorial
                    elif obj.name == "Tutorial_Zone":
                        self.interaction_zones[obj.name] = rect
                        print("ℹ️ Zona de Tutorial cargada")

            # Leemos las dos capas por si acaso
            try: cargar_interactivos(self.tmx_data.get_layer_by_name("Colisiones"))
            except: pass
            try: cargar_interactivos(self.tmx_data.get_layer_by_name("Interacciones"))
            except: pass
                    
        except ValueError:
            print("⚠️ Error leyendo capas de objetos")

        # --- SPAWN ---
        player_pos = (100, 100)
        try:
            spawn_obj = self.tmx_data.get_object_by_name("Spawn_Point")
            player_pos = (spawn_obj.x, spawn_obj.y)
        except:
            print("⚠️ No encontré Spawn_Point, usando (100,100)")

        # Crear Jugador
        self.player = Player(player_pos, [self.all_sprites], self.obstacle_rects)
        self.camera = Camera(self.map_width, self.map_height)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                
                # Interacción
                if event.key == pygame.K_e:
                    if self.state == "playing":
                        self.check_interaction()
                    elif self.state == "dialogue":
                        # Si estamos leyendo y apretamos E, cerramos el diálogo
                        self.state = "playing"

    def check_interaction(self):
        # Sensor un poquito más grande que Bob para detectar puertas cercanas
        bob_sensor = self.player.rect.inflate(20, 20)
        
        for name, zone_rect in self.interaction_zones.items():
            if bob_sensor.colliderect(zone_rect):
                print(f"✅ INTERACTUANDO CON: {name}")

                if name == "Tutorial_Zone":
                    self.state = "dialogue"
                    self.dialog_text = [
                        "Bienvenido a Student Souls.",
                        "Usa las FLECHAS para moverte.",
                        "Acércate a las puertas y presiona E para rendir.",
                        "Cuidado: Si tu dinero o cordura bajan a 0...",
                        "¡Pierdes la regularidad!"
                    ]
                
                # LÓGICA DE MINIJUEGOS (Aquí conectaremos los juegos después)
                elif name == "Aula_Runner":
                    print("--> ¡A CORRER!")
                elif name == "Aula_RPG":
                    print("--> PELEA CONTRA EL SISTEMA")
                elif name == "Aula_TP":
                    print("--> HACER EL TP")
                elif name == "Aula_Admin":
                    print("--> BUROCRACIA")

    def update(self):
        if self.state == "playing":
            self.all_sprites.update()
            self.camera.update(self.player)

    def draw_ui(self):
        # Dibuja los cartelitos "[E] Entrar"
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
                
                if msg:
                    # Fondo negro del cartel
                    text_surf = font.render(msg, True, color)
                    bg_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 20))
                    pygame.draw.rect(self.screen_native, (0,0,0), bg_rect.inflate(10, 4))
                    self.screen_native.blit(text_surf, bg_rect)
                    
                    # Debug visual (cuadro cyan sobre la puerta)
                    if self.debug_mode:
                        pygame.draw.rect(self.screen_native, (0, 255, 255), self.camera.apply_rect(zone_rect), 2)

    def draw_debug(self):
        if self.debug_mode:
            # Paredes (Rojo)
            for wall in self.obstacle_rects:
                pygame.draw.rect(self.screen_native, (255, 0, 0), self.camera.apply_rect(wall), 1)
            # Hitbox Bob (Verde)
            pygame.draw.rect(self.screen_native, (0, 255, 0), self.camera.apply_rect(self.player.hitbox), 1)

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
        
        for sprite in self.all_sprites:
            self.screen_native.blit(sprite.image, self.camera.apply(sprite))

        self.draw_debug()
        self.draw_ui() # <--- IMPORTANTE: Dibuja la interfaz al final
        self.draw_dialog()

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

    def draw_dialog(self):
        if self.state == "dialogue":
            # 1. Dibujar el fondo del cuadro (Azul estilo Final Fantasy o Negro simple)
            # Un rectángulo en la parte inferior de la pantalla
            margin = 20
            height = 90
            rect = pygame.Rect(margin, SCREEN_HEIGHT - height - margin, SCREEN_WIDTH - (margin*2), height)
            
            pygame.draw.rect(self.screen_native, (0, 0, 150), rect) # Fondo Azul
            pygame.draw.rect(self.screen_native, (255, 255, 255), rect, 2) # Borde Blanco
            
            # 2. Dibujar el texto
            font = pygame.font.SysFont("Arial", 12)
            y_offset = 10
            
            for line in self.dialog_text:
                text_surf = font.render(line, True, (255, 255, 255))
                self.screen_native.blit(text_surf, (rect.x + 10, rect.y + y_offset))
                y_offset += 15
                
            # 3. Indicador de "Continuar"
            press_e = font.render("[E] Cerrar", True, (255, 255, 0))
            self.screen_native.blit(press_e, (rect.right - 60, rect.bottom - 15))

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())