"""
PyGame renderer for the Cosmic Collision Lab simulation
"""
from typing import List, Tuple, Optional
import pygame
import numpy as np
import random
from physics.body import CelestialBody
from config import *


class Camera:
    """Camera system for panning and zooming"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.offset = np.array([width // 2, height // 2], dtype=float)
        self.zoom = 0.8  # Start zoomed out to see more of the solar system
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> np.ndarray:
        """Convert screen coordinates to world coordinates"""
        x, y = screen_pos
        world_x = (x - self.offset[0]) / self.zoom
        world_y = (y - self.offset[1]) / self.zoom
        return np.array([world_x, world_y], dtype=np.float64)
        
    def world_to_screen(self, world_pos: np.ndarray) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int(world_pos[0] * self.zoom + self.offset[0])
        screen_y = int(world_pos[1] * self.zoom + self.offset[1])
        return screen_x, screen_y
        
    def pan(self, delta: np.ndarray) -> None:
        """Pan the camera by delta pixels"""
        self.offset += delta
        
    def zoom_at(self, screen_pos: Tuple[int, int], zoom_factor: float) -> None:
        """Zoom in/out at a specific screen position"""
        # Get world position before zoom
        world_pos = self.screen_to_world(screen_pos)
        
        # Apply zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * zoom_factor))
        
        # Adjust offset to keep the world position under the cursor
        new_screen_pos = self.world_to_screen(world_pos)
        offset_delta = np.array(screen_pos) - np.array(new_screen_pos)
        self.offset += offset_delta


class StarField:
    """Background star field for visual appeal"""
    
    def __init__(self, width: int, height: int, num_stars: int = NUM_BACKGROUND_STARS):
        self.stars = []
        for _ in range(num_stars):
            x = random.randint(-width, width * 2)
            y = random.randint(-height, height * 2)
            size = random.randint(STAR_MIN_SIZE, STAR_MAX_SIZE)
            brightness = random.randint(100, 255)
            self.stars.append((x, y, size, brightness))
            
    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        """Draw the star field"""
        for x, y, size, brightness in self.stars:
            screen_x, screen_y = camera.world_to_screen(np.array([x, y], dtype=np.float64))
            
            # Only draw stars that are visible
            if (-10 < screen_x < screen.get_width() + 10 and 
                -10 < screen_y < screen.get_height() + 10):
                color = (brightness, brightness, brightness)
                pygame.draw.circle(screen, color, (screen_x, screen_y), size)


class Renderer:
    """Main rendering system for the simulation"""
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        pygame.init()
        pygame.font.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cosmic Collision Lab")
        
        # Camera system
        self.camera = Camera(width, height)
        
        # Star field
        self.star_field = StarField(width, height)
        
        # Fonts
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # UI state
        self.show_trails = True
        self.show_info = True
        self.show_fps = True
        
        # FPS tracking
        self.clock = pygame.time.Clock()
        self.fps_history = []
        
    def clear_screen(self) -> None:
        """Clear the screen with background color"""
        self.screen.fill(BACKGROUND_COLOR)
        
    def draw_star_field(self) -> None:
        """Draw the background star field"""
        self.star_field.draw(self.screen, self.camera)
        
    def draw_orbital_lines(self, bodies: List[CelestialBody]) -> None:
        """Draw orbital paths for planets around the sun"""
        # Find the sun (usually the most massive body at or near origin)
        sun = None
        for body in bodies:
            if body.name == "Sun" or body.mass > 500:  # Sun should have mass 1000
                sun = body
                break
                
        if not sun:
            return
            
        # Draw orbital circles for each planet
        sun_screen_pos = self.camera.world_to_screen(sun.position)
        
        for body in bodies:
            if body != sun and not body.merged and body.name != "Moon":
                # Calculate distance from sun
                distance = np.linalg.norm(body.position - sun.position)
                screen_radius = int(distance * self.camera.zoom)
                
                # Only draw if orbital line would be visible and reasonable size
                if 10 < screen_radius < self.width * 2:
                    pygame.draw.circle(self.screen, (50, 50, 50), sun_screen_pos, screen_radius, 1)

    def draw_bodies(self, bodies: List[CelestialBody]) -> None:
        """Draw all celestial bodies"""
        # Draw orbital lines first (behind bodies)
        self.draw_orbital_lines(bodies)
        
        # Sort bodies by distance to camera for proper rendering order
        sorted_bodies = sorted(bodies, key=lambda b: np.linalg.norm(b.position), reverse=True)
        
        for body in sorted_bodies:
            if not body.merged:
                self.draw_body(body)
                
    def draw_body(self, body: CelestialBody) -> None:
        """Draw a single celestial body using proper camera transformation"""
        if not body or body.merged:
            return
            
        # Check for valid position values
        if not np.isfinite(body.position).all():
            return
            
        # Convert world position to screen coordinates
        screen_pos = self.camera.world_to_screen(body.position)
        screen_radius = max(int(body.radius * self.camera.zoom), 2)
        
        # Check if body is visible on screen
        if (-100 < screen_pos[0] < self.width + 100 and 
            -100 < screen_pos[1] < self.height + 100):
            
            # Draw body
            pygame.draw.circle(self.screen, body.color, screen_pos, screen_radius)
            
            # Draw highlight ring for larger bodies
            if screen_radius > 10:
                highlight_color = tuple(min(255, int(c * 1.2)) for c in body.color)
                pygame.draw.circle(self.screen, highlight_color, screen_pos, screen_radius, 2)
                
            # Draw trail if enabled
            if body.trail_enabled and len(body.trail) > 1:
                trail_points = []
                for trail_x, trail_y in body.trail:
                    trail_screen_pos = self.camera.world_to_screen(np.array([trail_x, trail_y], dtype=np.float64))
                    # Check if trail point is on screen
                    if (-50 < trail_screen_pos[0] < self.width + 50 and 
                        -50 < trail_screen_pos[1] < self.height + 50):
                        trail_points.append(trail_screen_pos)
                
                # Draw trail as connected lines
                if len(trail_points) > 1:
                    trail_color = tuple(min(255, max(0, int(c * 0.6))) for c in body.color)
                    pygame.draw.lines(self.screen, trail_color, False, trail_points, max(1, int(self.camera.zoom)))
                
    def draw_ui_panel(self, stats: dict, selected_body: Optional[CelestialBody] = None) -> None:
        """Draw the enhanced information UI panel"""
        if not self.show_info:
            return
            
        # Panel background
        panel_width = 250
        panel_height = 220
        panel_rect = pygame.Rect(10, 10, panel_width, panel_height)
        
        # Semi-transparent background with gradient effect
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(190)
        panel_surface.fill((20, 25, 40))
        self.screen.blit(panel_surface, (10, 10))
        
        # Draw border with accent color
        pygame.draw.rect(self.screen, (80, 120, 200), panel_rect, 2)
        
        # Title
        title = self.font_medium.render("Simulation Info", True, (100, 200, 255))
        self.screen.blit(title, (20, 18))
        
        # Separator line
        pygame.draw.line(self.screen, (80, 120, 200), (20, 45), (panel_width - 10, 45), 1)
        
        # Draw statistics
        y_offset = 55
        
        # Status indicator
        status_text = "PAUSED" if stats.get('paused', False) else "RUNNING"
        status_color = (255, 200, 100) if stats.get('paused', False) else (100, 255, 150)
        status_surface = self.font_small.render(f"Status: {status_text}", True, status_color)
        self.screen.blit(status_surface, (20, y_offset))
        y_offset += 28
        
        # Main statistics
        text_lines = [
            f"Bodies: {stats.get('body_count', 0)}",
            f"FPS: {int(stats.get('fps', 0))}",
            f"Zoom: {self.camera.zoom:.2f}x",
            f"Energy: {stats.get('total_energy', 0):.2e}",
            f"Collisions: {stats.get('collision_count', 0)}"
        ]
            
        for line in text_lines:
            text_surface = self.font_small.render(line, True, (220, 220, 220))
            self.screen.blit(text_surface, (20, y_offset))
            y_offset += 26
            
        # Draw selected body info
        if selected_body:
            self.draw_selected_body_info(selected_body, panel_width + 20, 10)
            
    def draw_selected_body_info(self, body: CelestialBody, x: int, y: int) -> None:
        """Draw information about the selected body"""
        panel_width = 250
        panel_height = 150
        
        # Panel background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill(UI_BACKGROUND_COLOR)
        self.screen.blit(panel_surface, (x, y))
        
        # Draw border
        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        pygame.draw.rect(self.screen, UI_TEXT_COLOR, panel_rect, 2)
        
        # Draw body information
        y_offset = y + 15
        text_lines = [
            f"Selected: {body.name}",
            f"Mass: {body.mass:.2e} kg",
            f"Radius: {body.radius:.1f}",
            f"Position: ({body.position[0]:.1f}, {body.position[1]:.1f})",
            f"Velocity: {np.linalg.norm(body.velocity):.2f}",
            f"KE: {body.get_kinetic_energy():.2e}"
        ]
        
        for line in text_lines:
            text_surface = self.font_small.render(line, True, UI_TEXT_COLOR)
            self.screen.blit(text_surface, (x + 10, y_offset))
            y_offset += 20
            
    def draw_fps_counter(self) -> None:
        """Draw FPS counter"""
        if not self.show_fps:
            return
            
        # Calculate average FPS
        current_fps = self.clock.get_fps()
        self.fps_history.append(current_fps)
        if len(self.fps_history) > 30:  # Keep last 30 frames
            self.fps_history.pop(0)
            
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        
        # Draw FPS
        fps_text = f"FPS: {avg_fps:.1f}"
        text_surface = self.font_small.render(fps_text, True, UI_TEXT_COLOR)
        self.screen.blit(text_surface, (self.width - 100, 10))
        
    def draw_mouse_coordinates(self) -> None:
        """Draw current mouse coordinates in world space"""
        try:
            mouse_pos = pygame.mouse.get_pos()
            world_pos = self.camera.screen_to_world(np.array(mouse_pos, dtype=np.float64))
            
            coord_text = f"({world_pos[0]:.1f}, {world_pos[1]:.1f})"
            text_surface = self.font_small.render(coord_text, True, (200, 200, 200))
            self.screen.blit(text_surface, (self.width - 150, self.height - 30))
        except Exception as e:
            # Fallback if there's an issue with coordinate conversion
            error_text = "Coordinates unavailable"
            text_surface = self.font_small.render(error_text, True, (150, 150, 150))
            self.screen.blit(text_surface, (self.width - 150, self.height - 30))
        
    def draw_collision_flash(self, position: np.ndarray, intensity: float = 1.0) -> None:
        """Draw a collision flash effect"""
        screen_pos = self.camera.world_to_screen(position)
        screen_pos_int = (int(screen_pos[0]), int(screen_pos[1]))
        
        # Draw expanding circles with fading alpha
        for i in range(3):
            radius = int(30 * intensity * (i + 1))
            alpha = max(0, int(255 * intensity * (1 - i * 0.3)))
            
            # Create surface for alpha blending
            flash_surface = pygame.Surface((radius * 2, radius * 2))
            flash_surface.set_alpha(alpha)
            flash_color = (255, 255, 255) if i == 0 else (255, 200, 100)
            pygame.draw.circle(flash_surface, flash_color, (radius, radius), radius, 3)
            
            self.screen.blit(flash_surface, 
                           (screen_pos_int[0] - radius, screen_pos_int[1] - radius))
        
    def draw_crosshair(self, pos: Tuple[int, int]) -> None:
        """Draw crosshair at specified position"""
        x, y = pos
        size = 10
        color = (255, 255, 255)
        
        # Draw crosshair lines
        pygame.draw.line(self.screen, color, (x - size, y), (x + size, y), 2)
        pygame.draw.line(self.screen, color, (x, y - size), (x, y + size), 2)
        
    def draw_help_text(self) -> None:
        """Draw help text"""
        help_lines = [
            "Controls:",
            "Mouse Wheel: Zoom",
            "Right Click + Drag: Pan",
            "Left Click: Select/Drag Body",
            "Space: Pause/Resume",
            "R: Reset Simulation",
            "T: Toggle Trails",
            "I: Toggle Info",
            "F: Toggle FPS"
        ]
        
        y_start = self.height - len(help_lines) * 20 - 20
        
        for i, line in enumerate(help_lines):
            text_surface = self.font_small.render(line, True, UI_TEXT_COLOR)
            self.screen.blit(text_surface, (self.width - 200, y_start + i * 20))
            
    def update_display(self) -> None:
        """Update the display and maintain framerate"""
        pygame.display.flip()
        self.clock.tick(FPS)
        
    def handle_window_resize(self, new_size: Tuple[int, int]) -> None:
        """Handle window resize events"""
        self.width, self.height = new_size
        self.screen = pygame.display.set_mode(new_size)
        self.camera.width = self.width
        self.camera.height = self.height
        
    def get_mouse_world_pos(self) -> np.ndarray:
        """Get mouse position in world coordinates"""
        mouse_pos = pygame.mouse.get_pos()
        return self.camera.screen_to_world(mouse_pos)
        
    def toggle_trails(self) -> None:
        """Toggle trail visibility"""
        self.show_trails = not self.show_trails
        
    def toggle_info(self) -> None:
        """Toggle info panel visibility"""
        self.show_info = not self.show_info
        
    def toggle_fps(self) -> None:
        """Toggle FPS counter visibility"""
        self.show_fps = not self.show_fps
        
    def cleanup(self) -> None:
        """Clean up pygame resources"""
        pygame.quit()