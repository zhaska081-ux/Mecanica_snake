import pygame
import random
import sys

# --- 1. CONSTANTES DEL JUEGO ---
# Dimensiones de la ventana (basadas en el código original de 800x500)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500

# Tamaño de cada bloque (basado en MOVEMENT_STEP=20)
BLOCK_SIZE = 20

# Colores (RGB)
COLOR_BACKGROUND = (220, 220, 220)  # Gris claro (similar a #f0f0f0)
COLOR_SNAKE_HEAD = (0, 100, 0)      # Verde oscuro
COLOR_SNAKE_BODY = (0, 150, 0)      # Verde brillante
COLOR_APPLE = (255, 0, 0)           # Rojo
COLOR_TEXT = (51, 51, 51)           # Gris oscuro (similar a #333)

# Velocidad del juego (FPS o Ticks por segundo)
GAME_SPEED = 40 # 10 actualizaciones por segundo (similar a 75ms/tick)

# --- 2. CLASE COMIDA (FOOD) ---
class Food:
    """Maneja la posición aleatoria y el dibujo de la comida."""
    def __init__(self, surface):
        self.surface = surface
        self.rect = pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
        self.randomize_position()

    def randomize_position(self):
        """Coloca la comida en una posición aleatoria alineada a la cuadrícula."""
        # Calcula los límites máximos para la cuadrícula
        max_x = (WINDOW_WIDTH - BLOCK_SIZE) // BLOCK_SIZE
        max_y = (WINDOW_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE
        
        # Genera coordenadas de cuadrícula
        rand_x = random.randint(0, max_x) * BLOCK_SIZE
        rand_y = random.randint(0, max_y) * BLOCK_SIZE
        
        self.rect.topleft = (rand_x, rand_y)

    def draw(self):
        """Dibuja el bloque de comida."""
        pygame.draw.rect(self.surface, COLOR_APPLE, self.rect)


# --- 3. CLASE SERPIENTE (SNAKE) ---
class Snake:
    """Maneja el movimiento, el cuerpo y las colisiones de la serpiente."""
    def __init__(self, surface):
        self.surface = surface
        self.body = []
        
        # Posición inicial al centro (alineada a la cuadrícula)
        start_x = (WINDOW_WIDTH // 2) // BLOCK_SIZE * BLOCK_SIZE
        start_y = (WINDOW_HEIGHT // 2) // BLOCK_SIZE * BLOCK_SIZE
        
        # El cuerpo inicial es solo la cabeza
        self.body.append(pygame.Rect(start_x, start_y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Dirección inicial (Derecha por defecto)
        self.direction = (BLOCK_SIZE, 0) # (dx, dy)

    def change_direction(self, new_direction):
        """Actualiza la dirección si no intenta retroceder."""
        # (dx, dy) = dirección actual
        dx, dy = self.direction
        
        # new_direction es la tupla de movimiento (ej: (-BLOCK_SIZE, 0) para Izquierda)
        
        # Previene el retroceso inmediato (ej: si va a la derecha (20, 0) no puede ir a la izquierda (-20, 0))
        if new_direction[0] != -dx and new_direction[1] != -dy:
            self.direction = new_direction

    def move(self):
        """
        Calcula la nueva posición de la cabeza y actualiza el cuerpo.
        IMPLEMENTA LA ENVOLTURA DE LÍMITES (next_x % WINDOW_WIDTH).
        """
        # 1. Calcular la nueva posición de la cabeza
        head = self.body[0]
        dx, dy = self.direction
        
        next_x = head.left + dx
        next_y = head.top + dy

        # ⭐️ LÓGICA DE ENVOLTURA (TELETRANSPORTACIÓN) ⭐️
        # Usa el operador módulo (%) para teletransportar la serpiente al lado opuesto.
        # Esto replica con precisión: self.receive_movement_coords(next_x%800, next_y%500)
        new_x = next_x % WINDOW_WIDTH  # next_x % 800
        new_y = next_y % WINDOW_HEIGHT # next_y % 500
        
        # Nota: La lógica de Pygame Rect maneja implícitamente la alineación de la cuadrícula si las coordenadas 
        # son múltiplos de BLOCK_SIZE.
        
        new_head = pygame.Rect(new_x, new_y, BLOCK_SIZE, BLOCK_SIZE)
        
        # 2. Insertar la nueva cabeza y eliminar la cola (a menos que haya comido)
        self.body.insert(0, new_head)
        self.body.pop() # Elimina el último segmento (la cola)

    def grow(self):
        """Agrega un nuevo segmento al final del cuerpo."""
        # Simplemente insertamos una copia del último segmento. 
        # La próxima llamada a move() lo moverá al lugar correcto.
        #tail = self.body[-1]
        #self.body.append(tail) 

    # Se ha eliminado el método check_self_collision() para permitir que la serpiente
    # pase a través de sí misma sin terminar el juego.
    
    def draw(self):
        """Dibuja la serpiente, con un color diferente para la cabeza."""
        for i, segment in enumerate(self.body):
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(self.surface, color, segment)


# --- 4. FUNCIÓN PRINCIPAL DEL JUEGO ---
def game_loop():
    """Inicializa Pygame y ejecuta el bucle principal del juego."""
    pygame.init()
    
    # Configuración de la pantalla
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Wrapping (Pygame)")
    
    # Reloj para controlar el FPS/velocidad
    clock = pygame.time.Clock()
    
    # Fuente de texto
    font = pygame.font.Font(None, 36)
    
    # Inicializar objetos de juego
    snake = Snake(screen)
    food = Food(screen)
    score = 0
    # Como ya no hay colisiones, el juego nunca termina (game_over siempre es False)
    game_over = False 

    # --- BUCLE PRINCIPAL DEL JUEGO (GAME LOOP) ---
    running = True
    while running:
        # Controlar la velocidad de actualización
        clock.tick(GAME_SPEED)
        
        # --- Manejo de Eventos (Input) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and not game_over:
                # Mapeo de teclas de PyQt a tuplas de movimiento de Pygame
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -BLOCK_SIZE))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, BLOCK_SIZE))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-BLOCK_SIZE, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((BLOCK_SIZE, 0))
                # El reinicio por ESPACIO ya no es necesario, pero se mantiene la lógica si game_over fuera True por error
                elif event.key == pygame.K_SPACE and game_over: 
                    game_loop() # Reinicia la función principal
                    return # Sale de la función actual

        # --- Lógica de Juego (Solo si no ha terminado) ---
        if not game_over:
            snake.move()

            # 1. Colisión con la comida
            if snake.body[0].colliderect(food.rect):
                score += 1
                snake.grow()
                food.randomize_position()
                
            # 2. Colisión consigo misma: LÓGICA ELIMINADA. El juego no termina.
            # if snake.check_self_collision():
            #     game_over = True
            #     print("GAME OVER: ¡Colisión consigo mismo!")

        # --- Renderizado (Dibujo) ---
        screen.fill(COLOR_BACKGROUND)
        
        # Dibujar objetos
        food.draw()
        snake.draw()

        # Dibujar marcador
        score_text = font.render(f"Puntuación: {score}", True, COLOR_TEXT)
        screen.blit(score_text, (10, 10))
        
        # Dibujar mensaje de Game Over
        if game_over:
            game_over_text = font.render("JUEGO TERMINADO. Presiona ESPACIO para reiniciar.", True, (150, 0, 0))
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)

        # Actualizar la pantalla completa
        pygame.display.flip()

    # --- Finalización del juego ---
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    game_loop()
