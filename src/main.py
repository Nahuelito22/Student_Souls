import pygame
import asyncio
from scenes.level_hub import LevelHub
from scenes.level_entrance import LevelEntrance
from scenes.minigame_runner import MinigameRunner
from scenes.minigame_rpg import MinigameRPG

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

        # Empezamos en la calle
        self.current_scene = LevelEntrance(self.screen_native)

    async def run(self):
        while self.running:
            # 1. EVENTOS
            for event in pygame.event.get():
                # Cerrar con la X de la ventana
                if event.type == pygame.QUIT:
                    self.running = False
                
                # --- AQUÍ BORRAMOS EL ESCAPE GLOBAL ---
                # Ya no cerramos con ESC aquí, dejamos que la escena decida.
                
                # Pasamos el evento a la escena
                if hasattr(self.current_scene, "handle_input"):
                    # Si la escena devuelve True, significa "Cierra el juego por favor"
                    should_quit = self.current_scene.handle_input(event)
                    if should_quit:
                        self.running = False

            # 2. LOGICA DE CAMBIO DE ESCENA
            if hasattr(self.current_scene, "next_scene") and self.current_scene.next_scene:
                next_level = self.current_scene.next_scene
                
                if next_level == "Hub":
                    print("🔄 Volviendo al Hub...")
                    self.current_scene = LevelHub(self.screen_native)
                
                elif next_level == "Runner":
                    print("🏃 Iniciando Runner...")
                    self.current_scene = MinigameRunner(self.screen_native)

                elif next_level == "RPG": # <--- NUEVO
                    print("⚔️ Iniciando RPG...")
                    self.current_scene = MinigameRPG(self.screen_native)
                
                # (Aquí agregarás "Entrance" si quieres volver a la calle desde el Hub)

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