"""
Simple Cosmic Collision Lab - Basic Version
A basic 2D astrophysics simulator showing the initial project state
"""

import pygame
import numpy as np
import math
from typing import List, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
BACKGROUND_COLOR = (0, 0, 0)

# Physics constants (simplified)
G = 1.0  # Gravitational constant
TIME_SCALE = 0.1


class CelestialBody:
    """Simple celestial body with basic physics"""
    
    def __init__(self, x: float, y: float, mass: float, radius: float, color: tuple):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([0.0, 0.0], dtype=float)
        self.mass = mass
        self.radius = radius
        self.color = color
        self.trail = []
        
    def apply_force(self, force: np.ndarray) -> None:
        """Apply force to the body"""
        acceleration = force / self.mass
        self.velocity += acceleration * TIME_SCALE
        
    def update_position(self) -> None:
        """Update position based on velocity"""
        self.position += self.velocity * TIME_SCALE
        
        # Add to trail (keep last 100 points)
        self.trail.append(self.position.copy())
        if len(self.trail) > 100:
            self.trail.pop(0)
    
    def calculate_gravitational_force(self, other: 'CelestialBody') -> np.ndarray:
        """Calculate gravitational force between two bodies"""
        direction = other.position - self.position
        distance = np.linalg.norm(direction)
        
        if distance < self.radius + other.radius:
            return np.array([0.0, 0.0])
            
        # Avoid division by zero
        if distance < 1e-6:
            return np.array([0.0, 0.0])
            
        force_magnitude = G * self.mass * other.mass / (distance ** 2)
        force_direction = direction / distance
        
        return force_magnitude * force_direction


class SimplePhysicsEngine:
    """Basic physics engine for celestial mechanics"""
    
    def __init__(self):
        self.bodies: List[CelestialBody] = []
        self.paused = False
        
    def add_body(self, body: CelestialBody) -> None:
        """Add a body to the simulation"""
        self.bodies.append(body)
        
    def update(self) -> None:
        """Update physics simulation"""
        if self.paused:
            return
            
        # Calculate forces
        for i, body in enumerate(self.bodies):
            total_force = np.array([0.0, 0.0])
            
            for j, other in enumerate(self.bodies):
                if i != j:
                    force = body.calculate_gravitational_force(other)
                    total_force += force
                    
            body.apply_force(total_force)
            
        # Update positions
        for body in self.bodies:
            body.update_position()
            
    def toggle_pause(self) -> None:
        """Toggle simulation pause"""
        self.paused = not self.paused


class SimpleRenderer:
    """Basic renderer for the simulation"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.show_trails = True
        
    def clear_screen(self) -> None:
        """Clear the screen"""
        self.screen.fill(BACKGROUND_COLOR)
        
    def draw_body(self, body: CelestialBody) -> None:
        """Draw a celestial body"""
        # Draw trail
        if self.show_trails and len(body.trail) > 1:
            trail_points = [(int(p[0]), int(p[1])) for p in body.trail[-50:]]
            if len(trail_points) > 1:
                pygame.draw.lines(self.screen, (100, 100, 100), False, trail_points, 1)
        
        # Draw body
        pos = (int(body.position[0]), int(body.position[1]))
        pygame.draw.circle(self.screen, body.color, pos, int(body.radius))
        
        # Draw a small border
        pygame.draw.circle(self.screen, (255, 255, 255), pos, int(body.radius), 1)
        
    def draw_info(self, physics_engine: SimplePhysicsEngine) -> None:
        """Draw basic information"""
        info_text = [
            f"Bodies: {len(physics_engine.bodies)}",
            f"Status: {'Paused' if physics_engine.paused else 'Running'}",
            "",
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Reset",
            "T - Toggle Trails",
            "ESC - Quit"
        ]
        
        y_offset = 10
        for line in info_text:
            text_surface = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25


class SimpleCosmicCollisionLab:
    """Main application class for simple version"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Cosmic Collision Lab - Simple Version")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.physics_engine = SimplePhysicsEngine()
        self.renderer = SimpleRenderer(self.screen)
        
        # Create a simple solar system scenario
        self._create_simple_solar_system()
        
    def _create_simple_solar_system(self) -> None:
        """Create a basic solar system"""
        # Sun
        sun = CelestialBody(
            x=WINDOW_WIDTH // 2,
            y=WINDOW_HEIGHT // 2,
            mass=1000,
            radius=20,
            color=(255, 255, 0)
        )
        self.physics_engine.add_body(sun)
        
        # Earth
        earth = CelestialBody(
            x=WINDOW_WIDTH // 2 + 150,
            y=WINDOW_HEIGHT // 2,
            mass=50,
            radius=8,
            color=(0, 100, 255)
        )
        earth.velocity = np.array([0, 3.0])
        self.physics_engine.add_body(earth)
        
        # Mars
        mars = CelestialBody(
            x=WINDOW_WIDTH // 2 + 220,
            y=WINDOW_HEIGHT // 2,
            mass=30,
            radius=6,
            color=(255, 100, 50)
        )
        mars.velocity = np.array([0, 2.5])
        self.physics_engine.add_body(mars)
        
        # Jupiter
        jupiter = CelestialBody(
            x=WINDOW_WIDTH // 2 + 350,
            y=WINDOW_HEIGHT // 2,
            mass=200,
            radius=15,
            color=(255, 200, 100)
        )
        jupiter.velocity = np.array([0, 1.8])
        self.physics_engine.add_body(jupiter)
        
    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.physics_engine.toggle_pause()
                elif event.key == pygame.K_r:
                    self._reset_simulation()
                elif event.key == pygame.K_t:
                    self.renderer.show_trails = not self.renderer.show_trails
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    
    def _reset_simulation(self) -> None:
        """Reset the simulation"""
        self.physics_engine.bodies.clear()
        self._create_simple_solar_system()
        
    def update(self) -> None:
        """Update simulation"""
        self.physics_engine.update()
        
    def render(self) -> None:
        """Render the simulation"""
        self.renderer.clear_screen()
        
        # Draw all bodies
        for body in self.physics_engine.bodies:
            self.renderer.draw_body(body)
            
        # Draw UI
        self.renderer.draw_info(self.physics_engine)
        
        pygame.display.flip()
        
    def run(self) -> None:
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
            
        pygame.quit()


if __name__ == "__main__":
    app = SimpleCosmicCollisionLab()
    app.run()