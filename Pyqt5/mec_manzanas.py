import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel 
from PyQt5.QtCore import Qt
import random

# =================================================================
# CLASE 1: MECÁNICAS DE LA MANZANA (Apple Mechanics)
# Encapsula la lógica de posicionamiento aleatorio de la manzana.
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
        
        # Coloca la manzana inicialmente
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
