"""
Celestial body class for the physics simulation
"""
from typing import List, Tuple, Optional
import numpy as np
import pygame
from config import COLORS, MAX_TRAIL_LENGTH


class CelestialBody:
    """Represents a celestial body with physics properties"""
    
    def __init__(
        self,
        mass: float,
        position: np.ndarray,
        velocity: np.ndarray,
        radius: float,
        color: Tuple[int, int, int] = COLORS['planet'],
        name: str = "Body",
        body_id: Optional[str] = None
    ):
        self.mass = mass
        self.position = position.astype(np.float64).copy()
        self.velocity = velocity.astype(np.float64).copy()
        self.acceleration = np.zeros(2, dtype=np.float64)
        self.radius = radius
        self.color = color
        self.name = name
        self.id = body_id or f"body_{id(self)}"
        
        # Trail tracking
        self.trail: List[Tuple[float, float]] = []
        self.trail_enabled = True
        
        # Physics state
        self.forces = np.zeros(2)
        self.merged = False
        
    def add_force(self, force: np.ndarray) -> None:
        """Add a force to the current forces acting on the body"""
        self.forces += force.astype(np.float64)
        
    def update_physics(self, dt: float) -> None:
        """Update position and velocity based on current forces"""
        if self.merged:
            return
            
        # Calculate new acceleration from forces
        new_acceleration = self.forces / self.mass
        
        # Check for valid acceleration
        if not np.isfinite(new_acceleration).all():
            new_acceleration = np.zeros(2, dtype=np.float64)
        
        # Velocity Verlet integration for better orbital stability
        # v(t+dt/2) = v(t) + a(t) * dt/2
        # x(t+dt) = x(t) + v(t+dt/2) * dt  
        # v(t+dt) = v(t+dt/2) + a(t+dt) * dt/2
        
        # Update velocity to half-step
        self.velocity += self.acceleration * dt * 0.5
        
        # Update position using half-step velocity
        self.position += self.velocity * dt
        
        # Update velocity to full step using new acceleration
        self.velocity += new_acceleration * dt * 0.5
        
        # Store acceleration for next iteration
        self.acceleration = new_acceleration
        
        # Clamp extreme values to prevent overflow
        max_velocity = 1e6
        max_position = 1e6
        
        if np.linalg.norm(self.velocity) > max_velocity:
            self.velocity = self.velocity / np.linalg.norm(self.velocity) * max_velocity
            
        if np.linalg.norm(self.position) > max_position:
            self.position = self.position / np.linalg.norm(self.position) * max_position
            
        # Ensure all values are finite
        if not np.isfinite(self.velocity).all():
            self.velocity = np.zeros(2, dtype=np.float64)
        if not np.isfinite(self.position).all():
            self.position = np.zeros(2, dtype=np.float64)
        
        # Update trail
        if self.trail_enabled:
            self.trail.append((self.position[0], self.position[1]))
            if len(self.trail) > MAX_TRAIL_LENGTH:
                self.trail.pop(0)
        
        # Reset forces for next frame
        self.forces = np.zeros(2, dtype=np.float64)
        
    def get_kinetic_energy(self) -> float:
        """Calculate kinetic energy of the body"""
        return 0.5 * self.mass * np.linalg.norm(self.velocity) ** 2
        
    def get_momentum(self) -> np.ndarray:
        """Calculate momentum vector of the body"""
        return self.mass * self.velocity
        
    def distance_to(self, other: 'CelestialBody') -> float:
        """Calculate distance to another body"""
        return np.linalg.norm(self.position - other.position)
        
    def is_colliding_with(self, other: 'CelestialBody') -> bool:
        """Check if this body is colliding with another"""
        distance = self.distance_to(other)
        return distance < (self.radius + other.radius)
        
    def merge_with(self, other: 'CelestialBody') -> 'CelestialBody':
        """Merge this body with another (inelastic collision)"""
        # Conservation of momentum
        total_momentum = self.get_momentum() + other.get_momentum()
        total_mass = self.mass + other.mass
        new_velocity = total_momentum / total_mass
        
        # Conservation of mass (combine volumes)
        new_volume = (4/3) * np.pi * (self.radius**3 + other.radius**3)
        new_radius = ((3 * new_volume) / (4 * np.pi)) ** (1/3)
        
        # Weighted average position
        new_position = (self.position * self.mass + other.position * other.mass) / total_mass
        
        # Create new merged body
        merged_body = CelestialBody(
            mass=total_mass,
            position=new_position,
            velocity=new_velocity,
            radius=min(new_radius, 100),  # Cap radius for display
            color=self.color if self.mass > other.mass else other.color,
            name=f"{self.name}+{other.name}",
            body_id=f"merged_{self.id}_{other.id}"
        )
        
        # Mark original bodies as merged
        self.merged = True
        other.merged = True
        
        return merged_body
        
    def apply_gravitational_force(self, other: 'CelestialBody', G: float) -> None:
        """Apply gravitational force from another body"""
        if self.merged or other.merged or self == other:
            return
            
        # Calculate distance vector
        r_vector = other.position - self.position
        distance = np.linalg.norm(r_vector)
        
        # Avoid division by zero and extreme forces
        min_distance = max(self.radius + other.radius, 1.0)
        if distance < min_distance:
            return
            
        # Calculate gravitational force magnitude
        force_magnitude = G * self.mass * other.mass / (distance ** 2)
        
        # Limit maximum force to prevent numerical instability
        max_force = 1e20
        if force_magnitude > max_force:
            force_magnitude = max_force
        
        # Calculate unit vector and force vector
        if distance > 0:
            unit_vector = r_vector / distance
            force_vector = force_magnitude * unit_vector
            
            # Check for finite values
            if np.isfinite(force_vector).all():
                self.add_force(force_vector)
        
    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float], zoom: float) -> None:
        """Draw the body and its trail"""
        if self.merged:
            return
            
        # Calculate screen position
        screen_x = int((self.position[0] + camera_offset[0]) * zoom)
        screen_y = int((self.position[1] + camera_offset[1]) * zoom)
        screen_radius = max(int(self.radius * zoom), 2)
        
        # Draw trail
        if self.trail_enabled and len(self.trail) > 1:
            trail_points = []
            for i, (trail_x, trail_y) in enumerate(self.trail):
                trail_screen_x = int((trail_x + camera_offset[0]) * zoom)
                trail_screen_y = int((trail_y + camera_offset[1]) * zoom)
                
                # Check if point is on screen
                if (-50 < trail_screen_x < screen.get_width() + 50 and 
                    -50 < trail_screen_y < screen.get_height() + 50):
                    trail_points.append((trail_screen_x, trail_screen_y))
            
            # Draw trail as connected lines
            if len(trail_points) > 1:
                trail_color = tuple(min(255, max(0, int(c * 0.6))) for c in self.color)
                pygame.draw.lines(screen, trail_color, False, trail_points, max(1, int(zoom)))
        
        # Draw body
        if (-100 < screen_x < screen.get_width() + 100 and 
            -100 < screen_y < screen.get_height() + 100):
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), screen_radius)
            
            # Draw highlight ring for larger bodies
            if screen_radius > 10:
                highlight_color = tuple(min(255, int(c * 1.2)) for c in self.color)
                pygame.draw.circle(screen, highlight_color, (screen_x, screen_y), screen_radius, 2)
    
    def to_dict(self) -> dict:
        """Convert body to dictionary for API serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "mass": float(self.mass),
            "position": [float(self.position[0]), float(self.position[1])],
            "velocity": [float(self.velocity[0]), float(self.velocity[1])],
            "radius": float(self.radius),
            "color": list(self.color),
            "merged": self.merged
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CelestialBody':
        """Create body from dictionary"""
        return cls(
            mass=data["mass"],
            position=np.array(data["position"]),
            velocity=np.array(data["velocity"]),
            radius=data["radius"],
            color=tuple(data["color"]),
            name=data["name"],
            body_id=data["id"]
        )