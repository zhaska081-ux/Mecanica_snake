# =================================================================
# CLASE 2: VENTANA PRINCIPAL (Snake Mechanics & Game Core)
# Gestiona el movimiento de la serpiente, la puntuación y la colisión.
# =================================================================
class MainWindow(QMainWindow):
    """
    Window showing a snake movable by arrow keys and collision detection within 
    window limits.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snake Básico Refactorizado")
        
        # Game Constants
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 500
        self.LABEL_SIZE = 80 
        self.MOVEMENT_STEP = 20 # Pixels per movement
        
        self.set_window_size(width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT) 

        # Calculate central position, adjusted by emoji size
        center_x = (self.WINDOW_WIDTH // 2) - (self.LABEL_SIZE // 2)
        center_y = (self.WINDOW_HEIGHT // 2) - (self.LABEL_SIZE // 2)
        
        # Ensure initial position is aligned to the MOVEMENT_STEP grid
        self.current_x = (center_x // self.MOVEMENT_STEP) * self.MOVEMENT_STEP
        self.current_y = (center_y // self.MOVEMENT_STEP) * self.MOVEMENT_STEP

        # 1. Main Canvas Widget (No Layout)
        self.canvas = QWidget() 
        self.setCentralWidget(self.canvas)
        self.canvas.setStyleSheet("background-color: #f0f0f0;") 

        # 2. Create the Snake (QLabel)
        self.snake_label = QLabel("🐍", self.canvas) 
        self.snake_label.setStyleSheet("font-size: 80px;")
        self.snake_label.move(self.current_x, self.current_y)
        self.snake_label.show() 
        
        # 3. Create the Apple (QLabel)
        self.apple_label = QLabel("🍎", self.canvas) 
        self.apple_label.setStyleSheet("font-size: 80px;")
        self.apple_label.show()
        
        # ⭐️ INSTANCIACIÓN DE MECÁNICAS SEPARADAS
        self.apple_mechanics = AppleMechanics(
            self.canvas,
            self.apple_label,
            self.MOVEMENT_STEP,
            self.WINDOW_WIDTH,
            self.WINDOW_HEIGHT,
            self.LABEL_SIZE
        )
        
        # 4. Initialize the Counter and Score Label
        self.score = 0
        self.score_label = QLabel(f"Puntuación: {self.score}", self.canvas)
        self.score_label.setStyleSheet("font-size: 24px; color: white; background-color: #333; padding: 5px; border-radius: 5px;")
        self.score_label.move(10, 10) # Position in the top left corner
        self.score_label.show()
        
    def set_window_size(self, width, height, pos_x=100, pos_y=100):
        """Sets the size (width and height) and initial position of the window."""
        self.setGeometry(pos_x, pos_y, width, height)

    # FUNCTION TO CHECK LIMITS
    def limit_check(self, next_x, next_y):
        """
        Verifies if the next position (next_x, next_y) is within the window limits.
        """
        # Horizontal limits (X)
        is_x_valid = (next_x >= 0) and (next_x <= self.WINDOW_WIDTH - self.LABEL_SIZE)
        
        # Vertical limits (Y)
        is_y_valid = (next_y >= 0) and (next_y <= self.WINDOW_HEIGHT - self.LABEL_SIZE)
        
        if not is_x_valid or not is_y_valid:
            print("❌ INVALID MOVEMENT: Window limit reached.")
            return False
        
        return True

    # FUNCTION TO DETECT COLLISION AND UPDATE SCORE
    def check_collision_and_score(self):
        """
        Verifies if the snake has collided with the apple. If so,
        increments the score and repositions the apple (using AppleMechanics).
        """
        apple_x, apple_y = self.apple_mechanics.get_coords()
        
        # ⭐️ DEBUG: Print coordinates being compared
        print(f"➡️ Checking collision: Snake at ({self.current_x}, {self.current_y}) vs Apple at ({apple_x}, {apple_y})")
        
        # Check if the coordinates of the snake (current) and the apple (apple_x/y) are equal
        if self.current_x == apple_x and self.current_y == apple_y:
            self.score += 1
            self.score_label.setText(f"Puntuación: {self.score}")
            print(f"🎉 COLLISION! Current score: {self.score}")
            
            # Use the method from the separate mechanics class
            self.apple_mechanics.place_random_apple()

    def receive_movement_coords(self, new_x, new_y):
        """
        Receives the validated new coordinates and visually moves the snake.
        """
        # Update the internal position (state)
        self.current_x = new_x
        self.current_y = new_y
        
        # Visually move the QLabel to the new position
        self.snake_label.move(new_x, new_y) 
        
        # After moving the snake, check for collision
        self.check_collision_and_score()
        
        print(f"✅ Valid Movement: Snake moved to ({new_x}, {new_y})")
        
    def keyPressEvent(self, event):
        """
        Detects key presses, calculates the new position,
        and validates if it is within the limits before moving.
        """
        key = event.key()
        
        next_x = self.current_x
        next_y = self.current_y
        
        moved = False

        # 1. Calculate the potential next position
        if key == Qt.Key_Up:
            next_y -= self.MOVEMENT_STEP
            moved = True
        elif key == Qt.Key_Down:
            next_y += self.MOVEMENT_STEP
            moved = True
        elif key == Qt.Key_Left:
            next_x -= self.MOVEMENT_STEP
            moved = True
        elif key == Qt.Key_Right:
            next_x += self.MOVEMENT_STEP
            moved = True
        
        # If it was an arrow key, check and execute the movement
        if moved:
            if self.limit_check(next_x, next_y):
                # If the movement is valid, the movement function is called
                self.receive_movement_coords(next_x, next_y)
        else:
            super().keyPressEvent(event)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
