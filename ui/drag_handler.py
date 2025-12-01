"""
Drag and drop handler for celestial bodies
"""
import pygame
import numpy as np
from typing import Optional, Tuple, Callable
from physics.body import CelestialBody
from physics.physics_engine import PhysicsEngine


class DragHandler:
    """Handles dragging of celestial bodies in the simulation"""
    
    def __init__(self, physics_engine: PhysicsEngine, camera):
        self.physics_engine = physics_engine
        self.camera = camera
        
        # Drag mode control
        self.drag_mode_enabled = False
        
        # Drag state
        self.dragging_body: Optional[CelestialBody] = None
        self.drag_offset = np.array([0.0, 0.0], dtype=np.float64)
        self.original_velocity = np.array([0.0, 0.0], dtype=np.float64)
        self.drag_start_pos = np.array([0.0, 0.0], dtype=np.float64)
        self.drag_current_pos = np.array([0.0, 0.0], dtype=np.float64)
        
        # Visual properties
        self.drag_line_color = (255, 255, 100)
        self.selection_ring_color = (255, 255, 255)
        self.velocity_vector_color = (100, 255, 100)
        
        # Selection callback
        self.selection_callback: Optional[Callable[[Optional[CelestialBody]], None]] = None
        
    def set_selection_callback(self, callback: Callable[[Optional[CelestialBody]], None]) -> None:
        """Set callback for when body selection changes"""
        self.selection_callback = callback
        
    def set_drag_mode_enabled(self, enabled: bool) -> None:
        """Enable or disable drag mode"""
        self.drag_mode_enabled = enabled
        if not enabled and self.dragging_body:
            # End any current drag operation when disabling drag mode
            self.dragging_body = None
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle drag-related events, return True if event was consumed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._start_drag(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_body:
                return self._end_drag(event.pos)
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_body:
                return self._update_drag(event.pos)
                
        return False
        
    def _start_drag(self, mouse_pos: Tuple[int, int]) -> bool:
        """Start dragging operation or handle selection"""
        world_pos = self.camera.screen_to_world(mouse_pos)
        
        # Find body under cursor
        body = self._find_body_at_position(world_pos)
        
        if body:
            # Always notify selection callback when clicking on a body
            if self.selection_callback:
                self.selection_callback(body)
                
            # Only start dragging if drag mode is enabled
            if self.drag_mode_enabled:
                self.dragging_body = body
                self.drag_offset = body.position - world_pos
                self.original_velocity = body.velocity.copy()
                self.drag_start_pos = world_pos.copy()
                self.drag_current_pos = world_pos.copy()
                
                # Store original position for velocity calculation
                body._drag_start_time = pygame.time.get_ticks()
                body._drag_start_position = body.position.copy()
                
            return True
        else:
            # Clear selection if clicking on empty space
            if self.selection_callback:
                self.selection_callback(None)
                
        return False
        
    def _update_drag(self, mouse_pos: Tuple[int, int]) -> bool:
        """Update drag operation"""
        if not self.dragging_body or not self.drag_mode_enabled:
            return False
            
        world_pos = self.camera.screen_to_world(mouse_pos)
        self.drag_current_pos = world_pos.copy()
        
        # Update body position
        new_position = world_pos + self.drag_offset
        self.dragging_body.position = new_position
        
        # Calculate instantaneous velocity based on drag movement
        current_time = pygame.time.get_ticks()
        time_diff = (current_time - self.dragging_body._drag_start_time) / 1000.0  # Convert to seconds
        
        if time_diff > 0.01:  # Minimum time threshold to avoid division by zero
            displacement = new_position - self.dragging_body._drag_start_position
            drag_velocity = displacement / time_diff * 0.1  # Scale factor for reasonable velocities
            
            # Smooth the velocity to avoid jitter
            alpha = 0.3  # Smoothing factor
            self.dragging_body.velocity = (alpha * drag_velocity + 
                                         (1 - alpha) * self.dragging_body.velocity)
        
        return True
        
    def _end_drag(self, mouse_pos: Tuple[int, int]) -> bool:
        """End drag operation"""
        if not self.dragging_body or not self.drag_mode_enabled:
            return False
            
        # Final velocity calculation based on drag vector
        world_pos = self.camera.screen_to_world(mouse_pos)
        drag_vector = world_pos - self.drag_start_pos
        
        # Set velocity based on drag direction and distance
        velocity_scale = 0.5  # Adjust this to control how responsive dragging is
        final_velocity = drag_vector * velocity_scale
        
        # Limit maximum velocity to prevent extreme values
        max_velocity = 50.0
        velocity_magnitude = np.linalg.norm(final_velocity)
        if velocity_magnitude > max_velocity:
            final_velocity = final_velocity * (max_velocity / velocity_magnitude)
            
        self.dragging_body.velocity = final_velocity
        
        # Clean up drag attributes
        if hasattr(self.dragging_body, '_drag_start_time'):
            delattr(self.dragging_body, '_drag_start_time')
        if hasattr(self.dragging_body, '_drag_start_position'):
            delattr(self.dragging_body, '_drag_start_position')
            
        self.dragging_body = None
        return True
        
    def _find_body_at_position(self, world_pos: np.ndarray) -> Optional[CelestialBody]:
        """Find the topmost body at the given world position"""
        # Check bodies in reverse order (topmost first)
        for body in reversed(self.physics_engine.bodies):
            if body.merged:
                continue
                
            distance = np.linalg.norm(body.position - world_pos)
            # Use screen-space radius for more intuitive selection
            screen_radius = max(body.radius * self.camera.zoom, 10)  # Minimum 10px selection area
            world_radius = screen_radius / self.camera.zoom
            
            if distance <= world_radius:
                return body
                
        return None
        
    def get_selected_body(self) -> Optional[CelestialBody]:
        """Get the currently selected/dragged body"""
        return self.dragging_body
        
    def clear_selection(self) -> None:
        """Clear current selection"""
        if self.dragging_body:
            self.dragging_body = None
            if self.selection_callback:
                self.selection_callback(None)
                
    def draw_selection_indicators(self, screen: pygame.Surface, selected_body: Optional[CelestialBody]) -> None:
        """Draw visual indicators for selected and dragged bodies"""
        # Draw selection ring around selected body
        if selected_body and not selected_body.merged:
            # Check for valid position values
            if not (np.isfinite(selected_body.position).all()):
                return
                
            screen_pos = self.camera.world_to_screen(selected_body.position)
            screen_radius = max(int(selected_body.radius * self.camera.zoom), 10)
            
            # Validate screen coordinates
            if not (np.isfinite(screen_pos).all()):
                return
                
            # Draw selection ring
            pygame.draw.circle(screen, self.selection_ring_color, (int(screen_pos[0]), int(screen_pos[1])), 
                             screen_radius + 3, 2)
            
            # Draw velocity vector
            if np.linalg.norm(selected_body.velocity) > 0.1 and np.isfinite(selected_body.velocity).all():
                velocity_end = selected_body.position + selected_body.velocity * 10
                if np.isfinite(velocity_end).all():
                    velocity_screen_end = self.camera.world_to_screen(velocity_end)
                    if np.isfinite(velocity_screen_end).all():
                        screen_pos_tuple = (int(screen_pos[0]), int(screen_pos[1]))
                        velocity_screen_end_tuple = (int(velocity_screen_end[0]), int(velocity_screen_end[1]))
                        pygame.draw.line(screen, self.velocity_vector_color, 
                                       screen_pos_tuple, velocity_screen_end_tuple, 2)
                        # Draw arrowhead
                        self._draw_arrow_head(screen, screen_pos_tuple, velocity_screen_end_tuple, 
                                            self.velocity_vector_color)
        
        # Draw drag line if currently dragging
        if self.dragging_body and np.isfinite(self.drag_start_pos).all() and np.isfinite(self.drag_current_pos).all():
            start_screen = self.camera.world_to_screen(self.drag_start_pos)
            current_screen = self.camera.world_to_screen(self.drag_current_pos)
            
            if np.isfinite(start_screen).all() and np.isfinite(current_screen).all():
                # Draw drag line
                start_screen_tuple = (int(start_screen[0]), int(start_screen[1]))
                current_screen_tuple = (int(current_screen[0]), int(current_screen[1]))
                pygame.draw.line(screen, self.drag_line_color, start_screen_tuple, current_screen_tuple, 3)
            
            # Draw predicted velocity vector
            drag_vector = self.drag_current_pos - self.drag_start_pos
            velocity_scale = 0.5
            predicted_velocity = drag_vector * velocity_scale
            
            if np.linalg.norm(predicted_velocity) > 0.1:
                body_screen = self.camera.world_to_screen(self.dragging_body.position)
                velocity_end = self.dragging_body.position + predicted_velocity * 10
                velocity_screen_end = self.camera.world_to_screen(velocity_end)
                
                body_screen_tuple = (int(body_screen[0]), int(body_screen[1]))
                velocity_screen_end_tuple = (int(velocity_screen_end[0]), int(velocity_screen_end[1]))
                pygame.draw.line(screen, self.velocity_vector_color, 
                               body_screen_tuple, velocity_screen_end_tuple, 2)
                self._draw_arrow_head(screen, body_screen_tuple, velocity_screen_end_tuple, 
                                    self.velocity_vector_color)
                
    def _draw_arrow_head(self, screen: pygame.Surface, start: Tuple[int, int], 
                        end: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        """Draw an arrow head at the end of a line"""
        start_array = np.array(start, dtype=float)
        end_array = np.array(end, dtype=float)
        
        # Calculate direction vector
        direction = end_array - start_array
        length = np.linalg.norm(direction)
        
        if length < 10:  # Too short for arrow head
            return
            
        direction = direction / length
        
        # Arrow head parameters
        head_length = min(15, length * 0.3)
        head_angle = np.pi / 6  # 30 degrees
        
        # Calculate arrow head points
        perp = np.array([-direction[1], direction[0]], dtype=np.float64)
        
        head_point1 = end_array - head_length * (direction + np.sin(head_angle) * perp)
        head_point2 = end_array - head_length * (direction - np.sin(head_angle) * perp)
        
        # Draw arrow head
        points = [
            (int(end[0]), int(end[1])),
            (int(head_point1[0]), int(head_point1[1])),
            (int(head_point2[0]), int(head_point2[1]))
        ]
        pygame.draw.polygon(screen, color, points)


class CreationTool:
    """Tool for creating new celestial bodies"""
    
    def __init__(self, physics_engine: PhysicsEngine, camera):
        self.physics_engine = physics_engine
        self.camera = camera
        
        # Creation parameters
        self.default_mass = 5.972e24  # Earth mass
        self.default_radius = 15
        self.default_color = (100, 150, 255)
        
        # Creation mode state
        self.creation_mode = False
        self.creation_callback: Optional[Callable[[CelestialBody], None]] = None
        
    def set_creation_callback(self, callback: Callable[[CelestialBody], None]) -> None:
        """Set callback for when new body is created"""
        self.creation_callback = callback
        
    def set_creation_mode(self, enabled: bool) -> None:
        """Enable or disable creation mode"""
        self.creation_mode = enabled
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle creation-related events"""
        if not self.creation_mode:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click to create
                return self._create_body_at_position(event.pos)
                
        return False
        
    def _create_body_at_position(self, mouse_pos: Tuple[int, int]) -> bool:
        """Create a new body at the specified position"""
        world_pos = self.camera.screen_to_world(mouse_pos)
        
        # Create new body
        new_body = CelestialBody(
            mass=self.default_mass,
            position=world_pos.astype(np.float64),
            velocity=np.array([0.0, 0.0], dtype=np.float64),
            radius=self.default_radius,
            color=self.default_color,
            name=f"Body-{len(self.physics_engine.bodies) + 1}"
        )
        
        # Add to simulation
        self.physics_engine.add_body(new_body)
        
        # Notify callback
        if self.creation_callback:
            self.creation_callback(new_body)
            
        return True
        
    def set_default_properties(self, mass: float, radius: float, color: Tuple[int, int, int]) -> None:
        """Set default properties for newly created bodies"""
        self.default_mass = mass
        self.default_radius = radius
        self.default_color = color