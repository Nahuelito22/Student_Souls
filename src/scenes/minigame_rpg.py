import pygame
import os

# ==============================================================================
# ⚙️ CONFIGURACIÓN RPG
# ==============================================================================

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

# Posiciones (Ajustadas a tu gusto anterior)
PLAYER_POS = (70, 190) 
ENEMY_POS = (250, 180)

# Escalas visuales
PLAYER_SCALE = 1.5
ENEMY_SCALE = 1.5

# Colores
TEXT_COLOR = (255, 255, 255) # Blanco tiza
SELECTED_COLOR = (255, 255, 0) # Amarillo resaltador

class MinigameRPG:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.next_scene = None
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        
        # Estado del juego: "menu", "player_anim", "enemy_turn", "game_over", "win"
        self.state = "menu"
        
        # MENÚ
        self.menu_options = [
            {"name": "Chamuyar", "icon": "icon_attack.png"}, # Ataque
            {"name": "Tomar Café", "icon": "icon_coffee.png"}, # Curar / MP
            {"name": "Llorar", "icon": "icon_run.png"},      # Defensa / Skip (Usé run por ahora)
            {"name": "Abandonar", "icon": "icon_run.png"}    # Huir
        ]
        self.cursor_index = 0 # 0, 1, 2, 3
        
        # Cargar todo
        self.load_assets()

    def load_assets(self):
        base_path = os.path.join("game_assets", "graphics", "rpg")
        
        try:
            # --- ESCENARIO ---
            self.bg = pygame.image.load(os.path.join(base_path, "bg_battle.png")).convert()
            self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # --- PERSONAJES ---
            # Bob
            bob_img = pygame.image.load(os.path.join(base_path, "bob_battle_back.png")).convert_alpha()
            w, h = bob_img.get_size()
            self.bob_sprite = pygame.transform.scale(bob_img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
            
            # Enemigo
            enemy_img = pygame.image.load(os.path.join(base_path, "enemy_system.png")).convert_alpha()
            w, h = enemy_img.get_size()
            self.enemy_sprite = pygame.transform.scale(enemy_img, (int(w * ENEMY_SCALE), int(h * ENEMY_SCALE)))
            
            # --- UI (NUEVO) ---
            # Panel (Pizarrón)
            self.ui_panel = pygame.image.load(os.path.join(base_path, "ui_panel.png")).convert_alpha()
            # Escalamos el panel para que ocupe el ancho y unos 60px de alto
            self.ui_panel = pygame.transform.scale(self.ui_panel, (SCREEN_WIDTH, 70))
            
            # Cursor (Lapicera)
            self.ui_cursor = pygame.image.load(os.path.join(base_path, "ui_cursor.png")).convert_alpha()
            
            # Iconos
            self.icons = {}
            for opt in self.menu_options:
                name = opt["icon"]
                if name not in self.icons:
                    # Cargar icon
                    img = pygame.image.load(os.path.join(base_path, name)).convert_alpha()
                    self.icons[name] = img

        except Exception as e:
            print(f"❌ Error cargando assets RPG: {e}")
            # Fallbacks básicos
            self.bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg.fill((20, 20, 40))
            self.ui_panel = pygame.Surface((SCREEN_WIDTH, 70))
            self.ui_panel.fill((50, 30, 10))

        # Rectángulos para posicionar
        self.bob_rect = self.bob_sprite.get_rect(midbottom=PLAYER_POS)
        self.enemy_rect = self.enemy_sprite.get_rect(midbottom=ENEMY_POS)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_scene = "Hub"

            # --- CONTROL DEL MENÚ ---
            if self.state == "menu":
                # Mover cursor (Grilla 2x2)
                # 0: Chamuyar  1: Café
                # 2: Llorar    3: Huir
                
                if event.key == pygame.K_RIGHT:
                    if self.cursor_index == 0: self.cursor_index = 1
                    elif self.cursor_index == 2: self.cursor_index = 3
                    
                elif event.key == pygame.K_LEFT:
                    if self.cursor_index == 1: self.cursor_index = 0
                    elif self.cursor_index == 3: self.cursor_index = 2
                    
                elif event.key == pygame.K_DOWN:
                    if self.cursor_index == 0: self.cursor_index = 2
                    elif self.cursor_index == 1: self.cursor_index = 3
                    
                elif event.key == pygame.K_UP:
                    if self.cursor_index == 2: self.cursor_index = 0
                    elif self.cursor_index == 3: self.cursor_index = 1
                
                # Seleccionar opción
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.ejecutar_accion(self.cursor_index)

    def ejecutar_accion(self, index):
        print(f"👉 Elegiste: {self.menu_options[index]['name']}")
        # Aquí programaremos la lógica de ataque después
        # Por ahora solo imprime en consola

    def update(self):
        pass

    def draw(self):
        # 1. Escenario
        self.display_surface.blit(self.bg, (0, 0))
        self.display_surface.blit(self.bob_sprite, self.bob_rect)
        self.display_surface.blit(self.enemy_sprite, self.enemy_rect)
        
        # 2. UI Panel (Abajo)
        panel_y = SCREEN_HEIGHT - 70
        self.display_surface.blit(self.ui_panel, (0, panel_y))
        
        # 3. Opciones del Menú (Grilla 2x2)
        # Posiciones relativas dentro del panel
        start_x = 60
        start_y = panel_y + 15
        col_width = 140
        row_height = 25
        
        for i, option in enumerate(self.menu_options):
            # Calcular fila y columna (0,0), (1,0), (0,1), (1,1)
            col = i % 2
            row = i // 2
            
            x = start_x + (col * col_width)
            y = start_y + (row * row_height)
            
            # Color: Amarillo si está seleccionado
            color = SELECTED_COLOR if i == self.cursor_index else TEXT_COLOR
            
            # Dibujar Icono
            if option["icon"] in self.icons:
                icon_img = self.icons[option["icon"]]
                self.display_surface.blit(icon_img, (x - 20, y))
            
            # Dibujar Texto
            text_surf = self.font.render(option["name"], True, color)
            self.display_surface.blit(text_surf, (x, y))
            
            # Dibujar Cursor (La lapicera)
            if i == self.cursor_index:
                # La lapicera apunta al texto (un poco a la izquierda)
                self.display_surface.blit(self.ui_cursor, (x - 35, y + 2))