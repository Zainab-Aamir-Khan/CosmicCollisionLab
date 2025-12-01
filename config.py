"""
Configuration settings for Cosmic Collision Lab
"""
from typing import Tuple
import pygame

# Display settings
WINDOW_WIDTH: int = 1200
WINDOW_HEIGHT: int = 800
FPS: int = 60
BACKGROUND_COLOR: Tuple[int, int, int] = (5, 5, 15)

# Physics settings
GRAVITY_CONSTANT: float = 1.0  # Simple constant for stable simulation
SCALE_FACTOR: float = 1.0  # No scaling needed
TIME_SCALE: float = 0.08  # Faster time step for more visible orbital motion
MAX_TRAIL_LENGTH: int = 100
COLLISION_THRESHOLD: float = 0.8  # Collision occurs when distance < sum of radii * threshold

# UI settings
SLIDER_WIDTH: int = 200
SLIDER_HEIGHT: int = 20
BUTTON_WIDTH: int = 120
BUTTON_HEIGHT: int = 30
UI_MARGIN: int = 10
UI_BACKGROUND_COLOR: Tuple[int, int, int] = (30, 30, 40)
UI_TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)

# Object settings
MIN_MASS: float = 1.0
MAX_MASS: float = 1000.0
MIN_RADIUS: float = 5
MAX_RADIUS: float = 50
DEFAULT_MASS: float = 50.0  # Simple default mass
DEFAULT_RADIUS: float = 15

# Colors
COLORS = {
    'sun': (255, 255, 100),
    'planet': (100, 150, 255),
    'moon': (200, 200, 200),
    'asteroid': (150, 100, 50),
    'star': (255, 255, 255),
    'trail': (100, 100, 150)
}

# Star field settings
NUM_BACKGROUND_STARS: int = 200
STAR_MIN_SIZE: int = 1
STAR_MAX_SIZE: int = 3

# API settings
API_HOST: str = "localhost"
API_PORT: int = 8000