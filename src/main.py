import pygame
import asyncio
from scenes.level_hub import LevelHub

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

        # Iniciamos el Hub
        self.current_scene = LevelHub(self.screen_native)

    async def run(self): # <--- AQUÍ ESTABA EL ERROR (Faltaba 'async')
        while self.running:
            # 1. EVENTOS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # Pasar eventos a la escena
                if hasattr(self.current_scene, "handle_input"):
                    self.current_scene.handle_input(event)

            # 2. UPDATE
            self.current_scene.update()

            # 3. DRAW
            self.current_scene.draw()

            # 4. ESCALADO
            frame_scaled = pygame.transform.scale(self.screen_native, (SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
            self.screen_window.blit(frame_scaled, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(FPS)
            await asyncio.sleep(0) # Esto permite que funcione en web después

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())