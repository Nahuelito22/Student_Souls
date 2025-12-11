import pygame
import os
import random

# ==============================================================================
# ⚙️ CONFIGURACIÓN RPG
# ==============================================================================

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

# Posiciones
PLAYER_POS = (70, 190) 
ENEMY_POS = (250, 180)

# Escalas
PLAYER_SCALE = 1.5
ENEMY_SCALE = 1.5

# Colores
TEXT_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 255, 0)
HP_COLOR = (0, 255, 0)
HP_BG_COLOR = (100, 0, 0)

# Dificultad Global (Se puede guardar en un archivo después)
# Aumenta cada vez que ganas
CURRENT_DIFFICULTY_LEVEL = 1 

class MinigameRPG:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.next_scene = None
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 10, bold=True)
        
        # --- ESTADÍSTICAS ---
        # El enemigo escala con la dificultad
        self.max_hp_player = 100
        self.current_hp_player = 100
        
        base_enemy_hp = 80
        self.max_hp_enemy = base_enemy_hp + (CURRENT_DIFFICULTY_LEVEL * 20)
        self.current_hp_enemy = self.max_hp_enemy
        
        # Estado del juego: "menu", "player_anim", "enemy_turn", "enemy_anim", "win", "game_over"
        self.state = "menu"
        self.turn_text = f"Tu Turno (Nivel {CURRENT_DIFFICULTY_LEVEL})"
        
        # Variables de animación
        self.anim_timer = 0
        self.show_fx = None # "hit", "stress", "heal"
        self.fx_pos = (0, 0)

        # MENÚ
        self.menu_options = [
            {"name": "Chamuyar", "icon": "icon_attack.png"}, 
            {"name": "Tomar Café", "icon": "icon_coffee.png"}, 
            {"name": "Llorar", "icon": "icon_run.png"},      
            {"name": "Abandonar", "icon": "icon_run.png"}    
        ]
        self.cursor_index = 0
        
        self.load_assets()

    def load_assets(self):
        base_path = os.path.join("game_assets", "graphics", "rpg")
        try:
            # Escenario
            self.bg = pygame.image.load(os.path.join(base_path, "bg_battle.png")).convert()
            self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Personajes
            bob_img = pygame.image.load(os.path.join(base_path, "bob_battle_back.png")).convert_alpha()
            w, h = bob_img.get_size()
            self.bob_sprite = pygame.transform.scale(bob_img, (int(w * PLAYER_SCALE), int(h * PLAYER_SCALE)))
            
            enemy_img = pygame.image.load(os.path.join(base_path, "enemy_system.png")).convert_alpha()
            w, h = enemy_img.get_size()
            self.enemy_sprite = pygame.transform.scale(enemy_img, (int(w * ENEMY_SCALE), int(h * ENEMY_SCALE)))
            
            # UI
            self.ui_panel = pygame.image.load(os.path.join(base_path, "ui_panel.png")).convert_alpha()
            self.ui_panel = pygame.transform.scale(self.ui_panel, (SCREEN_WIDTH, 70))
            self.ui_cursor = pygame.image.load(os.path.join(base_path, "ui_cursor.png")).convert_alpha()
            
            # Iconos
            self.icons = {}
            for opt in self.menu_options:
                name = opt["icon"]
                if name not in self.icons:
                    self.icons[name] = pygame.image.load(os.path.join(base_path, name)).convert_alpha()

            # FX (Efectos)
            self.fx_hit = pygame.image.load(os.path.join(base_path, "fx_hit.png")).convert_alpha()
            self.fx_stress = pygame.image.load(os.path.join(base_path, "fx_stress.png")).convert_alpha() # Ojo con el nombre corregido

        except Exception as e:
            print(f"❌ Error assets RPG: {e}")
            self.bg = pygame.Surface((320, 240)); self.bg.fill((50,50,50))
            self.bob_sprite = pygame.Surface((32,32)); self.bob_sprite.fill((0,0,255))
            self.enemy_sprite = pygame.Surface((64,64)); self.enemy_sprite.fill((255,0,0))
            self.ui_panel = pygame.Surface((320,70)); self.ui_panel.fill((0,0,0))

        # Posiciones
        self.bob_rect = self.bob_sprite.get_rect(midbottom=PLAYER_POS)
        self.enemy_rect = self.enemy_sprite.get_rect(midbottom=ENEMY_POS)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            
            # --- MENU PRINCIPAL ---
            if self.state == "menu":
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
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.ejecutar_accion_jugador()

            # --- FIN DEL JUEGO ---
            elif self.state in ["win", "game_over"]:
                if event.key == pygame.K_SPACE:
                    self.next_scene = "Hub" # Volver al pasillo

    def ejecutar_accion_jugador(self):
        opcion = self.menu_options[self.cursor_index]["name"]
        
        if opcion == "Chamuyar":
            # Daño: Entre 15 y 25
            dmg = random.randint(15, 25)
            self.current_hp_enemy = max(0, self.current_hp_enemy - dmg)
            self.turn_text = f"¡Chamuyo efectivo! -{dmg} HP"
            
            # Configurar animación
            self.show_fx = "hit"
            self.fx_pos = self.enemy_rect.center
            self.state = "player_anim"
            self.anim_timer = pygame.time.get_ticks()

        elif opcion == "Tomar Café":
            heal = 30
            self.current_hp_player = min(self.max_hp_player, self.current_hp_player + heal)
            self.turn_text = "¡Qué rico café! +30 HP"
            self.state = "player_anim" # Usamos esto como delay
            self.show_fx = None # Podríamos poner un corazón
            self.anim_timer = pygame.time.get_ticks()

        elif opcion == "Llorar":
            self.turn_text = "Lloraste un rato... No pasó nada."
            self.state = "player_anim"
            self.show_fx = None
            self.anim_timer = pygame.time.get_ticks()

        elif opcion == "Abandonar":
            self.next_scene = "Hub"

    def update(self):
        now = pygame.time.get_ticks()

        # 1. ANIMACIÓN JUGADOR -> FIN TURNO
        if self.state == "player_anim":
            # Esperar 1 segundo viendo el efecto
            if now - self.anim_timer > 1000:
                self.show_fx = None
                if self.current_hp_enemy <= 0:
                    self.state = "win"
                    # AUMENTAR DIFICULTAD
                    global CURRENT_DIFFICULTY_LEVEL
                    CURRENT_DIFFICULTY_LEVEL += 1
                    self.turn_text = "¡APROBASTE! (Espacio para salir)"
                else:
                    self.state = "enemy_turn"
                    self.turn_text = "Turno del Sistema..."
                    self.anim_timer = now # Reset timer para el enemigo

        # 2. TURNO ENEMIGO (Pausa para pensar)
        elif self.state == "enemy_turn":
            if now - self.anim_timer > 1500: # 1.5 seg de espera
                # El enemigo ataca
                dmg = random.randint(10, 20) + (CURRENT_DIFFICULTY_LEVEL * 2)
                self.current_hp_player = max(0, self.current_hp_player - dmg)
                self.turn_text = f"¡El Sistema te golpeó! -{dmg} HP"
                
                self.show_fx = "stress"
                self.fx_pos = self.bob_rect.center
                self.state = "enemy_anim"
                self.anim_timer = now

        # 3. ANIMACIÓN ENEMIGO -> MENU
        elif self.state == "enemy_anim":
            if now - self.anim_timer > 1000:
                self.show_fx = None
                if self.current_hp_player <= 0:
                    self.state = "game_over"
                    self.turn_text = "RECURSAS LA MATERIA. (Espacio para salir)"
                else:
                    self.state = "menu"
                    self.turn_text = f"Tu Turno (Nivel {CURRENT_DIFFICULTY_LEVEL})"

    def draw_hp_bar(self, current, max_val, x, y, name):
        # Fondo rojo
        pygame.draw.rect(self.display_surface, HP_BG_COLOR, (x, y, 100, 10))
        # Barra verde
        ratio = current / max_val
        pygame.draw.rect(self.display_surface, HP_COLOR, (x, y, 100 * ratio, 10))
        # Borde
        pygame.draw.rect(self.display_surface, (255,255,255), (x, y, 100, 10), 1)
        # Texto
        txt = self.small_font.render(f"{name}: {current}/{max_val}", True, (255,255,255))
        self.display_surface.blit(txt, (x, y - 12))

    def draw(self):
        # 1. Escenario y Pjs
        self.display_surface.blit(self.bg, (0, 0))
        self.display_surface.blit(self.bob_sprite, self.bob_rect)
        self.display_surface.blit(self.enemy_sprite, self.enemy_rect)
        
        # 2. FX (Efectos sobre los personajes)
        if self.show_fx == "hit" and hasattr(self, "fx_hit"):
            rect = self.fx_hit.get_rect(center=self.fx_pos)
            self.display_surface.blit(self.fx_hit, rect)
        elif self.show_fx == "stress" and hasattr(self, "fx_stress"):
            rect = self.fx_stress.get_rect(center=self.fx_pos)
            self.display_surface.blit(self.fx_stress, rect)

        # 3. UI Panel
        panel_y = SCREEN_HEIGHT - 70
        self.display_surface.blit(self.ui_panel, (0, panel_y))
        
        # 4. Barras de Vida
        self.draw_hp_bar(self.current_hp_enemy, self.max_hp_enemy, 10, 10, "EL SISTEMA")
        self.draw_hp_bar(self.current_hp_player, self.max_hp_player, 210, 180, "BOB")

        # 5. Texto de Estado (Centro del panel)
        # Si no es menú, mostramos el mensaje de turno
        if self.state != "menu":
            text_surf = self.font.render(self.turn_text, True, SELECTED_COLOR)
            self.display_surface.blit(text_surf, (20, panel_y + 25))
        
        # 6. Opciones Menú (Solo si es tu turno)
        else:
            start_x = 60
            start_y = panel_y + 15
            col_width = 140
            row_height = 25
            
            for i, option in enumerate(self.menu_options):
                col = i % 2
                row = i // 2
                x = start_x + (col * col_width)
                y = start_y + (row * row_height)
                
                color = SELECTED_COLOR if i == self.cursor_index else TEXT_COLOR
                
                if option["icon"] in self.icons:
                    self.display_surface.blit(self.icons[option["icon"]], (x - 20, y))
                
                text_surf = self.font.render(option["name"], True, color)
                self.display_surface.blit(text_surf, (x, y))
                
                if i == self.cursor_index:
                    self.display_surface.blit(self.ui_cursor, (x - 35, y + 2))