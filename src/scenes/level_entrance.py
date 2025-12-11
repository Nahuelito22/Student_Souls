import pygame
from entities.player import Player

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
BG_COLOR = (100, 200, 255) # Azul Cielo

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
        # Cámara simple centrada
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        
        # Límites
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
        self.next_scene = None # Variable clave para cambiar de nivel
        self.debug_mode = False

        # Configurar el nivel "a mano" (Prototipo)
        self.setup_level()

    def setup_level(self):
        # Tamaño del mundo (Una calle larga)
        self.map_width = 600
        self.map_height = 240 # Igual al alto de pantalla

        # --- 1. CREAR SUELO Y PAREDES INVISIBLES ---
        # Pared Arriba (invisible)
        self.obstacle_rects.append(pygame.Rect(0, 0, 600, 100)) 
        # Pared Abajo (invisible)
        self.obstacle_rects.append(pygame.Rect(0, 200, 600, 40))
        # Pared Izquierda (Tope)
        self.obstacle_rects.append(pygame.Rect(-20, 0, 20, 240))
        
        # --- 2. CREAR PUERTAS (ZONAS) ---
        
        # Puerta Izquierda (McDonald's)
        rect_mc = pygame.Rect(20, 120, 60, 80)
        self.interaction_zones["Puerta_Mc"] = rect_mc
        
        # Puerta Derecha (Universidad)
        rect_uni = pygame.Rect(520, 120, 60, 80)
        self.interaction_zones["Puerta_Uni"] = rect_uni

        # --- 3. JUGADOR ---
        # Aparece en el medio de la calle
        self.player = Player((300, 150), [self.all_sprites], self.obstacle_rects)
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
                    print("🎓 Yendo a la Universidad...")
                    self.next_scene = "Hub" # <--- ESTO AVISA AL MAIN
                
                elif name == "Puerta_Mc":
                    print("🍔 Eligiendo la vida fácil...")
                    # Aquí podrías poner un Game Over o un diálogo
                    
    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw(self):
        self.display_surface.fill(BG_COLOR) # Cielo

        # Dibujar "Piso" (Calle)
        ground_rect = pygame.Rect(0, 100, self.map_width, 140)
        rect_visual = self.camera.apply_rect(ground_rect)
        pygame.draw.rect(self.display_surface, (100, 100, 100), rect_visual) # Gris asfalto

        # Dibujar Edificios (Placeholders)
        # Mc (Rojo)
        mc_rect = self.camera.apply_rect(self.interaction_zones["Puerta_Mc"])
        pygame.draw.rect(self.display_surface, (200, 0, 0), mc_rect)
        
        # Uni (Azul)
        uni_rect = self.camera.apply_rect(self.interaction_zones["Puerta_Uni"])
        pygame.draw.rect(self.display_surface, (0, 0, 200), uni_rect)

        # Sprites (Bob)
        for sprite in self.all_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))

        self.draw_ui()
        if self.debug_mode: self.draw_debug()

    def draw_ui(self):
        sensor = self.player.rect.inflate(20, 20)
        for name, rect in self.interaction_zones.items():
            if sensor.colliderect(rect):
                msg = ""
                if name == "Puerta_Uni": msg = "[E] Entrar a Cursar"
                if name == "Puerta_Mc": msg = "[E] Trabajar en Mc"
                
                if msg:
                    font = pygame.font.SysFont("Arial", 14, bold=True)
                    txt = font.render(msg, True, (255,255,255))
                    bg = txt.get_rect(midbottom=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 40))
                    pygame.draw.rect(self.display_surface, (0,0,0), bg.inflate(10,4))
                    self.display_surface.blit(txt, bg)

    def draw_debug(self):
        for r in self.obstacle_rects:
            pygame.draw.rect(self.display_surface, (255,0,0), self.camera.apply_rect(r), 1)
        for r in self.interaction_zones.values():
            pygame.draw.rect(self.display_surface, (0,255,255), self.camera.apply_rect(r), 2)
        pygame.draw.rect(self.display_surface, (0,255,0), self.camera.apply_rect(self.player.hitbox), 1)