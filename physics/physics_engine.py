"""
Physics engine for gravitational interactions and collision detection
"""
from typing import List, Tuple
import numpy as np
from physics.body import CelestialBody
from config import GRAVITY_CONSTANT, COLLISION_THRESHOLD


class PhysicsEngine:
    """Handles all physics calculations and interactions"""
    
    def __init__(self, gravity_constant: float = GRAVITY_CONSTANT):
        self.gravity_constant = gravity_constant
        self.bodies: List[CelestialBody] = []
        self.time_elapsed = 0.0
        self.paused = False
        self.collision_count = 0
        self.recent_collisions = []  # Track recent collisions for visual effects
        self.collision_count = 0  # Track total collisions
        
    def add_body(self, body: CelestialBody) -> None:
        """Add a body to the simulation"""
        self.bodies.append(body)
        
    def remove_body(self, body: CelestialBody) -> None:
        """Remove a body from the simulation"""
        if body in self.bodies:
            self.bodies.remove(body)
            
    def clear_bodies(self) -> None:
        """Clear all bodies from the simulation"""
        self.bodies.clear()
        self.time_elapsed = 0.0
        self.collision_count = 0
        
    def get_body_by_id(self, body_id: str) -> CelestialBody:
        """Get a body by its ID"""
        for body in self.bodies:
            if body.id == body_id:
                return body
        raise ValueError(f"Body with ID {body_id} not found")
        
    def update(self, dt: float) -> None:
        """Update all physics for one time step"""
        if self.paused:
            return
            
        # Calculate gravitational forces between all pairs
        self._calculate_gravitational_forces()
        
        # Check for collisions and handle mergers
        self._handle_collisions()
        
        # Update all body physics
        for body in self.bodies[:]:  # Use slice to avoid modification during iteration
            if not body.merged:
                body.update_physics(dt)
                
        # Remove merged bodies
        self.bodies = [body for body in self.bodies if not body.merged]
        
        # Update simulation time
        self.time_elapsed += dt
        
    def _calculate_gravitational_forces(self) -> None:
        """Calculate gravitational forces between all body pairs"""
        # Find the Sun (most massive body or named "Sun")
        sun = None
        for body in self.bodies:
            if body.name == "Sun" or body.mass > 2000:  # Sun should be much more massive
                sun = body
                break
        
        if sun:
            # Keep Sun fixed at origin for stability
            sun.position = np.array([0.0, 0.0], dtype=np.float64)
            sun.velocity = np.array([0.0, 0.0], dtype=np.float64)
            sun.net_force = np.array([0.0, 0.0], dtype=np.float64)
            
            # Calculate forces for all bodies (simplified without Moon complications)
            for body1 in self.bodies:
                if body1.merged or body1 == sun:
                    continue
                
                # Regular planets affected by Sun
                body1.apply_gravitational_force(sun, self.gravity_constant)
                
                # Apply forces between planets (but much weaker effect)
                for body2 in self.bodies:
                    if body2.merged or body2 == sun or body2 == body1:
                        continue
                    # Small planetary interactions
                    if body1.mass < 100 and body2.mass < 100:
                        body1.apply_gravitational_force(body2, self.gravity_constant * 0.1)
        else:
            # Fallback to original method if no sun found
            for i, body1 in enumerate(self.bodies):
                if body1.merged:
                    continue
                    
                for j, body2 in enumerate(self.bodies[i + 1:], i + 1):
                    if body2.merged:
                        continue
                        
                    # Apply gravitational force between the pair
                    body1.apply_gravitational_force(body2, self.gravity_constant)
                    body2.apply_gravitational_force(body1, self.gravity_constant)
                
    def _handle_collisions(self) -> None:
        """Check for collisions and merge bodies"""
        bodies_to_merge = []
        
        for i, body1 in enumerate(self.bodies):
            if body1.merged:
                continue
                
            for j, body2 in enumerate(self.bodies[i + 1:], i + 1):
                if body2.merged:
                    continue
                    
                # Check if bodies are colliding
                distance = body1.distance_to(body2)
                collision_distance = (body1.radius + body2.radius) * COLLISION_THRESHOLD
                
                if distance < collision_distance:
                    bodies_to_merge.append((body1, body2))
                    
        # Handle mergers
        for body1, body2 in bodies_to_merge:
            if not body1.merged and not body2.merged:
                # Record collision position for visual effects
                collision_pos = (body1.position + body2.position) / 2
                self.recent_collisions.append({
                    'position': collision_pos.copy(),
                    'time': self.time_elapsed,
                    'intensity': min(1.0, (body1.mass + body2.mass) / 1000.0)
                })
                
                merged_body = body1.merge_with(body2)
                self.collision_count += 1  # Track collisions
                self.bodies.append(merged_body)
                
    def get_total_energy(self) -> float:
        """Calculate total energy of the system"""
        kinetic_energy = sum(body.get_kinetic_energy() for body in self.bodies if not body.merged)
        potential_energy = self._calculate_potential_energy()
        return kinetic_energy + potential_energy
        
    def _calculate_potential_energy(self) -> float:
        """Calculate gravitational potential energy of the system"""
        potential = 0.0
        
        for i, body1 in enumerate(self.bodies):
            if body1.merged:
                continue
                
            for body2 in self.bodies[i + 1:]:
                if body2.merged:
                    continue
                    
                distance = body1.distance_to(body2)
                if distance > 0:
                    potential -= (self.gravity_constant * body1.mass * body2.mass) / distance
                    
        return potential
        
    def get_center_of_mass(self) -> np.ndarray:
        """Calculate center of mass of all bodies"""
        if not self.bodies:
            return np.zeros(2, dtype=np.float64)
            
        total_mass = sum(body.mass for body in self.bodies if not body.merged)
        if total_mass == 0:
            return np.zeros(2, dtype=np.float64)
            
        weighted_positions = sum(
            body.mass * body.position 
            for body in self.bodies 
            if not body.merged
        )
        
        return weighted_positions / total_mass
        
    def get_total_momentum(self) -> np.ndarray:
        """Calculate total momentum of the system"""
        active_bodies = [body for body in self.bodies if not body.merged]
        if not active_bodies:
            return np.zeros(2, dtype=np.float64)
        return sum(
            body.get_momentum() 
            for body in active_bodies
        )
        
    def get_average_velocity(self) -> float:
        """Calculate average speed of all bodies"""
        if not self.bodies:
            return 0.0
            
        active_bodies = [body for body in self.bodies if not body.merged]
        if not active_bodies:
            return 0.0
            
        total_speed = sum(np.linalg.norm(body.velocity) for body in active_bodies)
        return total_speed / len(active_bodies)
        
    def find_body_at_position(self, position: Tuple[float, float], tolerance: float = 10.0) -> CelestialBody:
        """Find a body at the given position (for mouse interaction)"""
        pos_array = np.array(position, dtype=np.float64)
        
        for body in self.bodies:
            if body.merged:
                continue
                
            distance = np.linalg.norm(body.position - pos_array)
            if distance <= body.radius + tolerance:
                return body
                
        return None
        
    def pause(self) -> None:
        """Pause the simulation"""
        self.paused = True
        
    def resume(self) -> None:
        """Resume the simulation"""
        self.paused = False
        
    def is_paused(self) -> bool:
        """Check if simulation is paused"""
        return self.paused
        
    def get_simulation_stats(self) -> dict:
        """Get comprehensive simulation statistics"""
        active_bodies = [body for body in self.bodies if not body.merged]
        
        stats = {
            "time_elapsed": self.time_elapsed,
            "body_count": len(active_bodies),
            "total_energy": self.get_total_energy(),
            "average_velocity": self.get_average_velocity(),
            "center_of_mass": self.get_center_of_mass().tolist(),
            "total_momentum": self.get_total_momentum().tolist(),
            "collision_count": self.collision_count,
            "paused": self.paused
        }
        
        return stats
        
    def get_recent_collisions(self, max_age: float = 2.0) -> list:
        """Get recent collisions for visual effects"""
        current_time = self.time_elapsed
        # Remove old collisions and return recent ones
        self.recent_collisions = [c for c in self.recent_collisions 
                                if current_time - c['time'] <= max_age]
        return self.recent_collisions