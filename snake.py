import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel 
from PyQt5.QtCore import Qt, QTimer
import random

# =================================================================
# CLASS 1: APPLE MECHANICS
# Encapsulates the random positioning logic for the apple.
# =================================================================
class AppleMechanics:
    def __init__(self, canvas, apple_label, movement_step, window_width, window_height, label_size):
        self.apple_label = apple_label
        self.canvas = canvas
        self.MOVEMENT_STEP = movement_step
        self.WINDOW_WIDTH = window_width
        self.WINDOW_HEIGHT = window_height
        self.LABEL_SIZE = label_size
        self.apple_x = 0
        self.apple_y = 0
        
        # Place the apple initially
        self.place_random_apple()
        
    def place_random_apple(self):
        """
        Places the apple widget in a random position 
        within the canvas limits, ensuring alignment with the movement grid.
        """
        # Calculate the maximum limits for the X and Y coordinates (adjusted by the label size)
        max_x = self.WINDOW_WIDTH - self.LABEL_SIZE
        max_y = self.WINDOW_HEIGHT - self.LABEL_SIZE
        
        # Generate random coordinates aligned to the grid (multiples of MOVEMENT_STEP)
        rand_x_steps = random.randint(0, max_x // self.MOVEMENT_STEP)
        rand_y_steps = random.randint(0, max_y // self.MOVEMENT_STEP)
        
        rand_x = rand_x_steps * self.MOVEMENT_STEP
        rand_y = rand_y_steps * self.MOVEMENT_STEP
        
        # Move the apple to the new random position
        self.apple_label.move(rand_x, rand_y)
        
        # STORE the apple's position for collision detection
        self.apple_x = rand_x
        self.apple_y = rand_y
        
        print(f"🍏 New Apple at: ({rand_x}, {rand_y})")

    def get_coords(self):
        """Returns the current absolute coordinates of the apple."""
        return self.apple_x, self.apple_y

# =================================================================
# CLASS 2: MAIN WINDOW (Snake Mechanics & Game Core)
# Manages snake movement, scoring, and collision.
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
        self.MOVEMENT_STEP = 20 # Pixels per movement (speed)
        
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
        
        # ⭐️ INSTANTIATION OF SEPARATE MECHANICS
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

        # ⭐️ QTIMER CONFIGURATION FOR CONTINUOUS MOVEMENT
        # Set initial direction to RIGHT so the snake moves immediately
        self.direction = Qt.Key_Right 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_snake_auto)
        self.timer.start(150) # Interval in ms (adjust to change speed)
        
    def set_window_size(self, width, height, pos_x=100, pos_y=100):
        """Sets the size (width and height) and initial position of the window."""
        self.setGeometry(pos_x, pos_y, width, height)

    # FUNCTION FOR CONTINUOUS MOVEMENT
    def move_snake_auto(self):
        """
        Automatically moves the snake in the stored direction (self.direction)
        on every timer tick.
        """
        if self.direction is None:
            return

        next_x = self.current_x
        next_y = self.current_y

        # 1. Calculate the potential next position based on the stored direction
        if self.direction == Qt.Key_Up:
            next_y -= self.MOVEMENT_STEP
        elif self.direction == Qt.Key_Down:
            next_y += self.MOVEMENT_STEP
        elif self.direction == Qt.Key_Left:
            next_x -= self.MOVEMENT_STEP
        elif self.direction == Qt.Key_Right:
            next_x += self.MOVEMENT_STEP

        # 2. Check limits and move
        if self.limit_check(next_x, next_y):
            self.receive_movement_coords(next_x, next_y)
        else:
            print("GAME OVER: ¡Límite alcanzado!")
            # If the game should end upon collision, uncomment:
            # self.timer.stop() 


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
        Detects key presses and updates the stored direction (self.direction).
        The movement continues via QTimer.
        """
        key = event.key()
        
        new_direction = None

        if key == Qt.Key_Up:
            if self.direction != Qt.Key_Down: # Prevent immediate reverse
                new_direction = key
        elif key == Qt.Key_Down:
            if self.direction != Qt.Key_Up: # Prevent immediate reverse
                new_direction = key
        elif key == Qt.Key_Left:
            if self.direction != Qt.Key_Right: # Prevent immediate reverse
                new_direction = key
        elif key == Qt.Key_Right:
            if self.direction != Qt.Key_Left: # Prevent immediate reverse
                new_direction = key
        
        if new_direction is not None:
            self.direction = new_direction
            
            # Execute the movement immediately to ensure responsiveness on first key press
            # The QTimer handles the continuous movement afterward.
            self.move_snake_auto()
        else:
            super().keyPressEvent(event)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
