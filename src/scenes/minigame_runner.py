import pygame
import random
import os

# ==============================================================================
# ⚙️ ZONA DE CONFIGURACIÓN Y DIFICULTAD (¡TOCA AQUÍ!)
# ==============================================================================

# --- PANTALLA ---
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
BG_COLOR = (135, 206, 235) 
GROUND_HEIGHT = 40
GROUND_COLOR = (100, 60, 20)

# --- VELOCIDAD ---
INITIAL_SPEED = 5        # Velocidad inicial (Menos de 4 es muy lento)
MAX_SPEED = 15           # Velocidad máxima permitida (Más de 20 es injugable)
SPEED_INCREMENT = 0.5    # Cuánto aumenta la velocidad en cada nivel
SCORE_TO_SPEED = 500     # Cada cuántos "puntos/metros" sube la velocidad

# --- SPAWN (ENEMIGOS) ---
BASE_SPAWN_DELAY = 1500  # Tiempo base entre enemigos (milisegundos)
MIN_SPAWN_DELAY = 600    # Tiempo mínimo (para que no sea imposible)

# --- SALUD MENTAL ---
MAX_HEALTH = 100         # Vida total
DAMAGE_HIT = 25          # Cuánto quita chocar un obstáculo
HEAL_RATE = 0.01         # Cuánto regenera por frame (0.01 lento, 0.1 rápido)

# --- POWER-UPS ---
POWERUP_CHANCE = 0.2     # Probabilidad (0.2 = 20%) de que aparezca un item
SHIELD_DURATION = 200    # Duración del escudo en frames (300 frames / 60 fps = 5 seg)

# ==============================================================================

class RunnerPlayer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # --- CARGAR IMÁGENES (RUTA CORREGIDA) ---
        # Ruta a la carpeta del runner
        path = os.path.join("game_assets", "graphics", "runner")
        
        # 1. CORRER (Bob_run_16x16.png - Tira horizontal de 384x32)
        self.run_frames = []
        try:
            run_sheet = pygame.image.load(os.path.join(path, "Bob_run_16x16.png")).convert_alpha()
            # La imagen tiene 384px de ancho. Cada frame mide 16px. 
            # Total frames = 384 / 16 = 24 frames.
            # Usaremos los primeros 6 frames que son de correr a la derecha.
            total_frames_to_load = 6
            for i in range(total_frames_to_load):
                # Recortamos horizontalmente: X varía, Y es siempre 0
                frame = pygame.Surface((16, 32), pygame.SRCALPHA)
                frame.blit(run_sheet, (0, 0), (i * 16, 0, 16, 32))
                self.run_frames.append(frame)
            print(f"✅ Cargados {len(self.run_frames)} frames de correr.")
                
        except Exception as e:
            print(f"⚠️ ERROR CARGANDO RUN: {e}")
            s = pygame.Surface((16, 32)); s.fill((0,0,255)); self.run_frames = [s]

        # 2. AGACHARSE (Bob_sit2_16x16.png - Tira horizontal)
        try:
            sit_sheet = pygame.image.load(os.path.join(path, "Bob_sit2_16x16.png")).convert_alpha()
            # Tomamos el primer frame de la tira (0,0)
            self.image_crouch = pygame.Surface((16, 32), pygame.SRCALPHA)
            self.image_crouch.blit(sit_sheet, (0, 0), (0, 0, 16, 32))
            print("✅ Imagen de agacharse cargada.")
            
        except Exception as e:
            print(f"⚠️ ERROR CARGANDO SIT: {e}")
            s = pygame.Surface((16, 16)); s.fill((0,255,255)); self.image_crouch = s

        # --- CONFIGURACIÓN INICIAL ---
        self.frame_index = 0
        self.animation_speed = 0.2
        
        # Empezamos con el primer frame de correr
        self.image = self.run_frames[0]
        self.rect = self.image.get_rect()
        
        # Posición
        self.rect.x = 40
        self.ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.rect.bottom = self.ground_y
        
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
        elif self.is_jumping:
            # Frame fijo al saltar (usamos el 3ro que suele ser piernas abiertas)
            idx = 2 if len(self.run_frames) > 2 else 0
            self.image = self.run_frames[idx]
        else:
            # Corriendo
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.run_frames):
                self.frame_index = 0
            self.image = self.run_frames[int(self.frame_index)]

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
        
        if self.type == 0: # Bolsa Dinero
            width, height = 25, 25
            y_pos = SCREEN_HEIGHT - GROUND_HEIGHT
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 215, 0), (0, 5, width, height - 5))
            pygame.draw.circle(self.image, (200, 165, 0), (width//2, 5), width//2)
            
        elif self.type == 1: # PDF Viejo
            width, height = 30, 40
            y_pos = SCREEN_HEIGHT - GROUND_HEIGHT
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 200, 200), (0, 0, width, height))
            pygame.draw.rect(self.image, (100, 100, 100), (5, 5, width-10, height-10), 2)
            
        elif self.type == 2: # Visto/Pájaro
            width, height = 40, 20
            color = (150, 150, 255)
            # 50% probabilidad de venir bajo (saltar) o alto (agacharse)
            if random.random() < 0.5:
                y_pos = SCREEN_HEIGHT - GROUND_HEIGHT - 10 # Bajo
            else:
                y_pos = SCREEN_HEIGHT - GROUND_HEIGHT - 35 # Alto (Cara)
                
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, color, (0, 0, width, height))

        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(10, 50)
        self.rect.bottom = y_pos

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0: self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type):
        super().__init__()
        self.type = power_type
        
        if self.type == 0: # Café (Velocidad)
            width, height = 20, 20
            color = (139, 69, 19)
            self.effect = "speed"
            
        elif self.type == 1: # Escudo
            width, height = 25, 25
            color = (0, 255, 0)
            self.effect = "shield"

        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(10, 50)
        self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT - random.randint(20, 60)

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0: self.kill()

class MinigameRunner:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.font = pygame.font.SysFont("Arial", 16)
        
        # INICIAR EL JUEGO LIMPIO
        self.reset_game()

    def reset_game(self):
        """Reinicia todas las variables para jugar de nuevo sin recargar la clase"""
        self.state = "playing"
        self.next_scene = None

        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.player = RunnerPlayer()
        self.all_sprites.add(self.player)

        # Variables de estado
        self.mental_health = MAX_HEALTH
        self.game_speed = INITIAL_SPEED
        self.score = 0
        self.spawn_timer = 0
        self.spawn_delay = BASE_SPAWN_DELAY
        
        self.player_shield = False
        self.shield_timer = 0
        
        self.ground_x = 0
        
        # Fondo Parallax
        self.bg_layers = []
        self.bg_speeds = [0.2, 0.5, 0.8]
        self.bg_x_positions = [0, 0, 0]
        for i in range(3):
            layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))
            layer.fill((135 - i*20, 206 - i*20, 235 - i*20))
            # Nubes aleatorias
            for j in range(3):
                pygame.draw.ellipse(layer, (255, 255, 255, 100), (random.randint(0, 300), random.randint(0, 150), 60, 20))
            self.bg_layers.append(layer)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            
            # --- JUGANDO ---
            if self.state == "playing":
                # Salto (Espacio, W, Flecha Arriba)
                if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                    self.player.jump()
                # Agacharse (S, Flecha Abajo)
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.player.crouch()
                # Salir al Hub con ESC
                if event.key == pygame.K_ESCAPE:
                    self.next_scene = "Hub"
            
            # --- GAME OVER ---
            elif self.state == "game_over":
                if event.key == pygame.K_SPACE:
                    self.reset_game() # Reinicio limpio
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
            # 1. Dificultad Progresiva
            if self.score > 0 and self.score % SCORE_TO_SPEED == 0:
                if self.game_speed < MAX_SPEED:
                    self.game_speed += SPEED_INCREMENT
                    print(f"⚡ ¡Velocidad: {self.game_speed:.1f}!")

            # 2. Scroll Suelo
            self.ground_x -= self.game_speed
            if self.ground_x <= -SCREEN_WIDTH:
                self.ground_x = 0
            
            # 3. Scroll Fondo (Parallax)
            for i in range(3):
                self.bg_x_positions[i] -= self.game_speed * self.bg_speeds[i]
                if self.bg_x_positions[i] <= -SCREEN_WIDTH: self.bg_x_positions[i] = 0

            # 4. Spawner Enemigos
            now = pygame.time.get_ticks()
            # Fórmula: A más velocidad, menos espera
            current_delay = max(MIN_SPAWN_DELAY, BASE_SPAWN_DELAY - (self.game_speed * 50))
            
            if now - self.spawn_timer > self.spawn_delay:
                self.spawn_timer = now
                self.spawn_delay = random.randint(int(current_delay), int(current_delay) + 1000)
                
                # Elegir obstáculo (50% normal, 30% doble, 20% volador)
                roll = random.random()
                obs_type = 0 if roll < 0.5 else 1 if roll < 0.8 else 2
                
                new_obs = Obstacle(obs_type)
                self.all_sprites.add(new_obs)
                self.obstacles.add(new_obs)

                # Spawner Power-ups
                if random.random() < POWERUP_CHANCE:
                    new_pw = PowerUp(random.choice([0, 1]))
                    self.all_sprites.add(new_pw)
                    self.powerups.add(new_pw)

            # 5. Updates
            self.player.update()
            self.obstacles.update(self.game_speed)
            self.powerups.update(self.game_speed)

            # 6. Colisiones Power-ups
            hits_pw = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for p in hits_pw:
                if p.effect == "speed": # Café
                    self.score += 500 # Premio de puntaje
                    self.mental_health = min(self.mental_health + 20, MAX_HEALTH) # Cura
                elif p.effect == "shield": # Resumen
                    self.player_shield = True
                    self.shield_timer = SHIELD_DURATION

            # Actualizar Escudo
            if self.player_shield:
                self.shield_timer -= 1
                if self.shield_timer <= 0: self.player_shield = False

            # 7. Colisiones Enemigos
            if not self.player_shield:
                hits = pygame.sprite.spritecollide(self.player, self.obstacles, True) # True = desaparece al chocar
                if hits:
                    self.mental_health -= DAMAGE_HIT
                    if self.mental_health <= 0:
                        self.state = "game_over"

            # 8. Regeneración
            if self.mental_health < MAX_HEALTH:
                self.mental_health += HEAL_RATE

            self.score += 1

    def draw(self):
        # Fondo
        for i, layer in enumerate(self.bg_layers):
            x = self.bg_x_positions[i]
            self.display_surface.blit(layer, (x, 0))
            self.display_surface.blit(layer, (x + SCREEN_WIDTH, 0))

        # Suelo
        pygame.draw.rect(self.display_surface, GROUND_COLOR, (self.ground_x, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(self.display_surface, GROUND_COLOR, (self.ground_x + SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        # Sprites
        self.all_sprites.draw(self.display_surface)
        
        # Escudo Visual
        if self.player_shield:
            pygame.draw.circle(self.display_surface, (0,255,255), self.player.rect.center, 20, 2)

        # UI
        self.display_surface.blit(self.font.render(f"Distancia: {self.score//10}m", True, (0,0,0)), (10, 10))
        
        # Barra de Vida
        pygame.draw.rect(self.display_surface, (50,50,50), (10, 35, 100, 10))
        life_w = int(100 * (self.mental_health / MAX_HEALTH))
        col = (0,255,0) if self.mental_health > 50 else (255,0,0)
        pygame.draw.rect(self.display_surface, col, (10, 35, life_w, 10))

        # Game Over
        if self.state == "game_over":
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(150); s.fill((0,0,0))
            self.display_surface.blit(s, (0,0))
            
            cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
            t1 = self.font.render("¡REPROBADO!", True, (255, 50, 50))
            t2 = self.font.render("[ESPACIO] Recuperatorio", True, (255, 255, 255))
            t3 = self.font.render("[ESC] Abandonar", True, (200, 200, 200))
            
            self.display_surface.blit(t1, t1.get_rect(center=(cx, cy-20)))
            self.display_surface.blit(t2, t2.get_rect(center=(cx, cy+10)))
            self.display_surface.blit(t3, t3.get_rect(center=(cx, cy+30)))