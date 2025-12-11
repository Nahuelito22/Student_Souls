import pygame
import asyncio
from scenes.level_hub import LevelHub
from scenes.level_entrance import LevelEntrance # <--- IMPORTAR LA NUEVA ESCENA

# --- CONFIGURACIÓN ---
SCREEN_WIDTH = 320   
SCREEN_HEIGHT = 240
SCALE_FACTOR = 3    
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen_window = pygame.display.set_mode((SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
        self.screen_native = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Student Souls: Veintipico Edition")
        self.clock = pygame.time.Clock()
        self.running = True

        # --- GESTOR DE ESCENAS ---
        # AHORA EMPEZAMOS EN LA ENTRADA (CALLE)
        self.current_scene = LevelEntrance(self.screen_native)

    async def run(self):
        while self.running:
            # 1. EVENTOS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                
                if hasattr(self.current_scene, "handle_input"):
                    self.current_scene.handle_input(event)

            # 2. LOGICA DE CAMBIO DE ESCENA
            # Verificamos si la escena actual quiere cambiar
            if hasattr(self.current_scene, "next_scene") and self.current_scene.next_scene:
                next_level = self.current_scene.next_scene
                
                if next_level == "Hub":
                    print("🎬 Entrando a la Facultad...")
                    self.current_scene = LevelHub(self.screen_native)
                
                # Aquí agregaríamos más cambios (ej: volver a la calle)
                
            # 3. UPDATE
            self.current_scene.update()

            # 4. DRAW
            self.current_scene.draw()

            # 5. ESCALADO
            frame_scaled = pygame.transform.scale(self.screen_native, (SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
            self.screen_window.blit(frame_scaled, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(FPS)
            await asyncio.sleep(0)

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())