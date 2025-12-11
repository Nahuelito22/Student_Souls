import pygame
import random
import os

# ==============================================================================
# ⚙️ CONFIGURACIÓN DEL MINIJUEGO
# ==============================================================================

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
GROUND_HEIGHT = 40
BG_COLOR = (135, 206, 235) # Color de respaldo si falla la imagen

# DIFICULTAD
INITIAL_SPEED = 5        
MAX_SPEED = 15           
SPEED_INCREMENT = 0.5    
SCORE_TO_SPEED = 500     

# SPAWN
BASE_SPAWN_DELAY = 1500  
MIN_SPAWN_DELAY = 600    

# SALUD
MAX_HEALTH = 100         
DAMAGE_HIT = 25          
HEAL_RATE = 0.01         

# POWER-UPS
POWERUP_CHANCE = 0.2     
SHIELD_DURATION = 300    

# ==============================================================================

class RunnerPlayer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Ruta base
        path = os.path.join("game_assets", "graphics", "runner")
        
        # --- 1. CARGAR CORRER (Bob_run_16x16.png) ---
        self.run_frames = []
        try:
            # Tira horizontal de 384x32
            run_sheet = pygame.image.load(os.path.join(path, "Bob_run_16x16.png")).convert_alpha()
            # Usamos los primeros 6 frames (0 a 5)
            for i in range(6):
                frame = pygame.Surface((16, 32), pygame.SRCALPHA)
                frame.blit(run_sheet, (0, 0), (i * 16, 0, 16, 32))
                self.run_frames.append(frame)
        except Exception as e:
            print(f"⚠️ Error cargando Run: {e}")
            s = pygame.Surface((16, 32)); s.fill((50, 50, 255)); self.run_frames = [s]

        # --- 2. CARGAR AGACHARSE (Bob_sit2_16x16.png) ---
        try:
            sit_sheet = pygame.image.load(os.path.join(path, "Bob_sit2_16x16.png")).convert_alpha()
            # Detectamos la altura real de la imagen para recortar bien
            # Si el sheet mide 16px de alto, recortamos 16x16. Si mide 32, 16x32.
            h = sit_sheet.get_height() 
            self.image_crouch = pygame.Surface((16, h), pygame.SRCALPHA)
            self.image_crouch.blit(sit_sheet, (0, 0), (0, 0, 16, h)) # Frame 0
        except Exception as e:
            print(f"⚠️ Error cargando Sit: {e}")
            s = pygame.Surface((16, 16)); s.fill((50, 100, 255)); self.image_crouch = s

        # Configuración Inicial
        self.frame_index = 0
        self.animation_speed = 0.25
        
        self.image = self.run_frames[0]
        self.rect = self.image.get_rect()
        
        self.rect.x = 40
        self.ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.rect.bottom = self.ground_y
        
        # Hitbox Ajustada (Más delgada para ser amable con el jugador)
        self.hitbox = self.rect.inflate(-6, -5)
        
        # Físicas
        self.gravity = 0.8
        self.jump_power = -12
        self.velocity_y = 0
        self.is_jumping = False
        self.is_crouching = False

    def update(self):
        # Gravedad
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Colisión suelo
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.velocity_y = 0
            self.is_jumping = False

        # --- ANIMACIÓN ---
        if self.is_crouching:
            self.image = self.image_crouch
            # Ajuste de hitbox al agacharse
            self.hitbox = self.rect.inflate(-6, -5)
            self.hitbox.bottom = self.rect.bottom
        elif self.is_jumping:
            # Frame de salto (el 3ro suele ser piernas abiertas)
            idx = 2 if len(self.run_frames) > 2 else 0
            self.image = self.run_frames[idx]
            self.hitbox = self.rect.inflate(-6, -5)
            self.hitbox.bottom = self.rect.bottom
        else:
            # Corriendo
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.run_frames):
                self.frame_index = 0
            self.image = self.run_frames[int(self.frame_index)]
            # Ajuste constante de hitbox
            self.hitbox = self.rect.inflate(-6, -5)
            self.hitbox.bottom = self.rect.bottom

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            if self.is_crouching: self.stand_up()

    def stop_jump(self):
        if self.is_jumping and self.velocity_y < -3:
            self.velocity_y = -3

    def crouch(self):
        if not self.is_crouching:
            self.is_crouching = True
            old_bottom = self.rect.bottom
            old_x = self.rect.x
            
            self.image = self.image_crouch
            self.rect = self.image.get_rect()
            
            # Restaurar posición
            self.rect.bottom = old_bottom
            self.rect.x = old_x
            
            if self.is_jumping: self.velocity_y = 10

    def stand_up(self):
        if self.is_crouching:
            self.is_crouching = False
            old_bottom = self.rect.bottom
            old_x = self.rect.x
            
            self.image = self.run_frames[0]
            self.rect = self.image.get_rect()
            
            self.rect.bottom = old_bottom
            self.rect.x = old_x

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type):
        super().__init__()
        self.type = obs_type
        path = os.path.join("game_assets", "graphics", "runner")
        
        image_name = ""
        # Fallbacks
        width, height = 30, 30
        y_pos = SCREEN_HEIGHT - GROUND_HEIGHT
        
        if self.type == 0: # Bolsa Dinero
            image_name = "obstacle_money.png"
            width, height = 25, 38
            
        elif self.type == 1: # PDF Viejo
            image_name = "obstacle_pdf.png"
            width, height = 25, 31
            
        elif self.type == 2: # Pájaro/Visto
            image_name = "obstacle_bird.png"
            width, height = 30, 30
            # Altura variable (Bajo o Alto)
            if random.random() < 0.5:
                y_pos = SCREEN_HEIGHT - GROUND_HEIGHT - 5 # Bajo
            else:
                y_pos = SCREEN_HEIGHT - GROUND_HEIGHT - 35 # Alto

        # Cargar
        try:
            self.image = pygame.image.load(os.path.join(path, image_name)).convert_alpha()
        except:
            # Placeholder si falta la imagen
            self.image = pygame.Surface((width, height))
            self.image.fill((255,0,0) if self.type != 2 else (255,255,0))

        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(10, 50)
        self.rect.bottom = y_pos
        
        # Hitbox un poco más chica que el dibujo para ser justa
        self.hitbox = self.rect.inflate(-4, -4)

    def update(self, speed):
        self.rect.x -= speed
        self.hitbox.center = self.rect.center # Sincronizar hitbox
        if self.rect.right < 0: self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type):
        super().__init__()
        self.type = power_type
        path = os.path.join("game_assets", "graphics", "runner")
        
        image_name = ""
        if self.type == 0: # Café
            image_name = "item_coffee.png"
            self.effect = "speed"
        elif self.type == 1: # Escudo
            self.effect = "shield"
            # Elegir uno random de los 3 escudos
            variantes = ["item_shield1.png", "item_shield2.png", "item_shield3.png"]
            image_name = random.choice(variantes)

        try:
            self.image = pygame.image.load(os.path.join(path, image_name)).convert_alpha()
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((0,255,0))

        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(10, 50)
        self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT - random.randint(30, 80)

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0: self.kill()

class MinigameRunner:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.font = pygame.font.SysFont("Arial", 16)
        self.reset_game()

    def reset_game(self):
        self.state = "playing"
        self.next_scene = None

        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.player = RunnerPlayer()
        self.all_sprites.add(self.player)

        # Variables Estado
        self.mental_health = MAX_HEALTH
        self.game_speed = INITIAL_SPEED
        self.score = 0
        self.spawn_timer = 0
        self.spawn_delay = BASE_SPAWN_DELAY
        self.player_shield = False
        self.shield_timer = 0
        
        # --- CARGAR FONDOS (PARALLAX) ---
        path = os.path.join("game_assets", "graphics", "runner")
        try:
            # Capa 1: Cielo
            self.bg_sky = pygame.image.load(os.path.join(path, "bg_sky.png")).convert()
            self.bg_sky = pygame.transform.scale(self.bg_sky, (SCREEN_WIDTH, SCREEN_HEIGHT))

            # Capa 2: Ciudad
            self.bg_city = pygame.image.load(os.path.join(path, "bg_city.png")).convert_alpha()
            self.bg_city = pygame.transform.scale(self.bg_city, (SCREEN_WIDTH, SCREEN_HEIGHT))

            # Capa 3: Suelo (AQUÍ ESTABA EL PROBLEMA)
            self.bg_ground = pygame.image.load(os.path.join(path, "bg_ground.png")).convert_alpha()
            # Forzamos que mida 320x40 para que llene el hueco negro
            self.bg_ground = pygame.transform.scale(self.bg_ground, (SCREEN_WIDTH, SCREEN_HEIGHT))

        except Exception as e:
            print(f"⚠️ Error fondos: {e}")
            # Fallbacks
            self.bg_sky = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.bg_sky.fill(BG_COLOR)
            self.bg_city = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            self.bg_ground = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT)); self.bg_ground.fill((100, 60, 20))

        # Posiciones de scroll
        self.x_sky = 0
        self.x_city = 0
        self.x_ground = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "playing":
                if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                    self.player.jump()
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.player.crouch()
                if event.key == pygame.K_ESCAPE:
                    self.next_scene = "Hub"
            
            elif self.state == "game_over":
                if event.key == pygame.K_SPACE:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.next_scene = "Hub"

        if event.type == pygame.KEYUP:
            if self.state == "playing":
                if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                    self.player.stop_jump()
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.player.stand_up()

    def update(self):
        if self.state == "playing":
            # 1. Dificultad
            if self.score > 0 and self.score % SCORE_TO_SPEED == 0:
                if self.game_speed < MAX_SPEED:
                    self.game_speed += SPEED_INCREMENT
                    print(f"⚡ ¡Velocidad: {self.game_speed:.1f}!")

            # 2. Scroll Parallax (Movemos cada capa a distinta velocidad)
            # Cielo: 10% velocidad
            self.x_sky -= self.game_speed * 0.1
            if self.x_sky <= -SCREEN_WIDTH: self.x_sky = 0
            
            # Ciudad: 50% velocidad
            self.x_city -= self.game_speed * 0.5
            if self.x_city <= -SCREEN_WIDTH: self.x_city = 0
            
            # Suelo: 100% velocidad
            self.x_ground -= self.game_speed
            if self.x_ground <= -SCREEN_WIDTH: self.x_ground = 0

            # 3. Spawner
            now = pygame.time.get_ticks()
            current_delay = max(MIN_SPAWN_DELAY, BASE_SPAWN_DELAY - (self.game_speed * 50))
            
            if now - self.spawn_timer > self.spawn_delay:
                self.spawn_timer = now
                self.spawn_delay = random.randint(int(current_delay), int(current_delay) + 1000)
                
                # Obstáculos
                roll = random.random()
                obs_type = 0 if roll < 0.5 else 1 if roll < 0.8 else 2
                new_obs = Obstacle(obs_type)
                self.all_sprites.add(new_obs)
                self.obstacles.add(new_obs)

                # Power-ups
                if random.random() < POWERUP_CHANCE:
                    new_pw = PowerUp(random.choice([0, 1]))
                    self.all_sprites.add(new_pw)
                    self.powerups.add(new_pw)

            # 4. Updates
            self.player.update()
            self.obstacles.update(self.game_speed)
            self.powerups.update(self.game_speed)

            # 5. Colisiones Powerups
            hits_pw = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for p in hits_pw:
                if p.effect == "speed": # Café
                    self.score += 500
                    self.mental_health = min(self.mental_health + 20, MAX_HEALTH)
                elif p.effect == "shield": # Escudo
                    self.player_shield = True
                    self.shield_timer = SHIELD_DURATION

            if self.player_shield:
                self.shield_timer -= 1
                if self.shield_timer <= 0: self.player_shield = False

            # 6. Colisiones Obstáculos (Usando la hitbox mejorada del player)
            # spritecollide usa .rect por defecto, pero podemos chequear colisión manual si queremos precisión extrema.
            # Por ahora usamos collide_rect normal pero como ajustamos .inflate en el player, funciona bien.
            if not self.player_shield:
                for obs in self.obstacles:
                    # Chequeo preciso: hitbox vs hitbox
                    if self.player.hitbox.colliderect(obs.hitbox):
                        self.mental_health -= DAMAGE_HIT
                        obs.kill() # El obstáculo desaparece al pegar
                        if self.mental_health <= 0:
                            self.state = "game_over"

            # 7. Regeneración
            if self.mental_health < MAX_HEALTH:
                self.mental_health += HEAL_RATE

            self.score += 1

    def draw(self):
        # Función auxiliar para dibujar infinito
        def draw_infinite(image, x_pos, y_pos):
            self.display_surface.blit(image, (x_pos, y_pos))
            self.display_surface.blit(image, (x_pos + SCREEN_WIDTH, y_pos))

        # 1. Dibujar Fondos (Orden: Cielo -> Ciudad -> Suelo)
        draw_infinite(self.bg_sky, self.x_sky, 0)
        draw_infinite(self.bg_city, self.x_city, 0)

        ground_offset_y = 20 
        draw_infinite(self.bg_ground, self.x_ground, ground_offset_y)

        # 2. Sprites
        self.all_sprites.draw(self.display_surface)
        
        # Escudo Visual
        if self.player_shield:
            pygame.draw.circle(self.display_surface, (0,255,255), self.player.rect.center, 20, 2)

        # 3. UI
        # Distancia
        self.display_surface.blit(self.font.render(f"Distancia: {self.score//10}m", True, (0,0,0)), (10, 10))
        
        # Barra Vida
        bar_x, bar_y = 10, 30
        pygame.draw.rect(self.display_surface, (50,50,50), (bar_x, bar_y, 100, 10))
        life_w = int(100 * (self.mental_health / MAX_HEALTH))
        col = (0,255,0) if self.mental_health > 50 else (255,255,0) if self.mental_health > 25 else (255,0,0)
        pygame.draw.rect(self.display_surface, col, (bar_x, bar_y, life_w, 10))
        
        # Game Over
        if self.state == "game_over":
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(150); s.fill((0,0,0))
            self.display_surface.blit(s, (0,0))
            
            cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
            t1 = self.font.render("¡REPROBADO!", True, (255, 50, 50))
            t2 = self.font.render("[ESPACIO] Recuperatorio", True, (255, 255, 255))
            t3 = self.font.render("[ESC] Volver al Hub", True, (200, 200, 200))
            
            self.display_surface.blit(t1, t1.get_rect(center=(cx, cy-20)))
            self.display_surface.blit(t2, t2.get_rect(center=(cx, cy+10)))
            self.display_surface.blit(t3, t3.get_rect(center=(cx, cy+30)))