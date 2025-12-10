import pygame
import random
import time

# --- 1. CONFIGURACIÓN INICIAL DE PYGAME ---
pygame.init()

# Colores (R, G, B)
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50) # Nuevo color para el mensaje de victoria

# Configuración de la Pantalla
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Juego del Cuadrado Comedor (7s)")

# Reloj para controlar la velocidad del juego
clock = pygame.time.Clock()
FPS = 60 # Frames por segundo

# Fuente para el texto
font = pygame.font.Font(None, 36)

# Variable de estado de victoria
is_winner = False

# --- 2. CLASE JUGADOR (PLAYER) ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 30
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.score = 0

    def update(self, keys):
        # Manejo de la entrada del teclado
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Limitar movimiento dentro de los bordes
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

# --- 3. CLASE OBJETIVO (TARGET) ---
class Target(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 30
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        # Generar en una posición aleatoria lejos de los bordes
        margin = 30
        self.rect.x = random.randrange(margin, SCREEN_WIDTH - margin - self.size)
        self.rect.y = random.randrange(margin, SCREEN_HEIGHT - margin - self.size)

# --- 4. FUNCIONES DE JUEGO ---

def reset_game():
    """Reinicia todas las variables del juego."""
    global player, target, all_sprites, start_time, game_over, is_winner
    
    # Crear sprites
    player = Player()
    target = Target()
    
    # Grupo de sprites
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(target)
    
    # Temporizador
    start_time = time.time()
    game_over = False
    is_winner = False # Asegurar que el estado de victoria se reinicie

def display_message(text, color, y_offset=0, size=36):
    """Muestra un mensaje centrado en la pantalla."""
    temp_font = pygame.font.Font(None, size)
    text_surface = temp_font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)

# --- 5. BUCLE PRINCIPAL DEL JUEGO ---

def game_loop():
    global start_time, game_over, is_winner

    running = True
    reset_game()

    while running:
        # --- Manejo de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    
        keys = pygame.key.get_pressed()

        if not game_over:
            # --- Actualización de la Lógica del Juego ---
            
            # 1. Mover Jugador
            player.update(keys)

            # 2. Comprobar Colisión
            if pygame.sprite.collide_rect(player, target):
                player.score += 1
                player.size += 7.5 # Opcional: El jugador crece ligeramente
                
                # Para redibujar el cuadrado con el nuevo tamaño
                player.image = pygame.Surface([player.size, player.size])
                player.image.fill(BLUE)
                player.rect = player.image.get_rect(center=player.rect.center)
                
                # **LÓGICA DE VICTORIA AÑADIDA**
                if player.score >= 10:
                    is_winner = True
                    game_over = True
                else:
                    target.spawn() # Nuevo objetivo solo si aún no has ganado
                    start_time = time.time() # Reiniciar el temporizador

            # 3. Gestionar Temporizador
            time_limit = 5.0
            elapsed_time = time.time() - start_time
            time_left = time_limit - elapsed_time

            if time_left <= 0:
                game_over = True # Derrota por tiempo

            # --- Dibujo ---
            screen.fill(WHITE)
            all_sprites.draw(screen)

            # Dibujar estadísticas
            score_text = font.render(f"Comidos: {player.score} / 10", True, BLACK)
            screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

            # Dibujar el tiempo restante
            display_time = max(0.0, time_left)
            time_color = BLACK
            if display_time <= 2.0:
                time_color = RED # Rojo si queda poco tiempo
            
            time_text = font.render(f"Tiempo: {display_time:.1f}s", True, time_color)
            screen.blit(time_text, (10, 10))
            
            if display_time <= 2.0 and int(time.time() * 2) % 2 == 0:
                 # Efecto de parpadeo para el tiempo restante
                 time_text_warning = font.render(f"¡Rápido! :()", True, time_color)
                 screen.blit(time_text_warning, (10, 40))


        else:
            # --- Pantalla de Fin de Juego (Derrota o Victoria) ---
            screen.fill(BLACK)
            
            if is_winner:
                # Mensaje de Victoria
                display_message("¡GANASTE! :)", GREEN, -30, 48)
                display_message(f"¡Comiste los {player.score} cuadrados a tiempo!", WHITE, 30, 36)
            else:
                # Mensaje de Derrota por Tiempo
                display_message("¡FIN DEL JUEGO! :(", RED, -30, 48)
                display_message(f"Solo lograste comer: {player.score} cuadrados.", WHITE, 30, 36)
                
            display_message("Presiona ESPACIO para reiniciar.", WHITE, 70, 28)


        # Actualizar la pantalla completa
        pygame.display.flip()

        # Limitar los frames por segundo
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game_loop()