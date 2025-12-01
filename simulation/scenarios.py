"""
Predefined cosmic scenarios for the simulation
"""
import numpy as np
from typing import List
from physics.body import CelestialBody
from config import COLORS


class ScenarioManager:
    """Manages predefined cosmic scenarios"""
    
    @staticmethod
    def create_solar_system() -> List[CelestialBody]:
        """Create a simplified solar system scenario"""
        bodies = []
        
        # Sun (at center) - much more massive for stability
        sun = CelestialBody(
            mass=5000.0,  # Much larger mass for stability
            position=np.array([0.0, 0.0], dtype=np.float64),
            velocity=np.array([0.0, 0.0], dtype=np.float64),
            radius=40,  # Larger radius to make it more visible
            color=COLORS['sun'],
            name="Sun"
        )
        bodies.append(sun)
        
        # Planetary data: [name, distance, mass, radius, orbital_velocity, color] - calculated for stable orbits
        # Orbital velocity = sqrt(G * M_sun / distance) where G=1.0, M_sun=5000.0
        import math
        G = 1.0
        sun_mass = 5000.0  # Updated to match new sun mass
        
        planets_data = [
            ("Mercury", 100, 8.0, 6, math.sqrt(G * sun_mass / 100), (169, 169, 169)),
            ("Venus", 140, 12.0, 8, math.sqrt(G * sun_mass / 140), (255, 198, 73)),
            ("Earth", 180, 15.0, 10, math.sqrt(G * sun_mass / 180), (100, 149, 237)),
            ("Mars", 240, 10.0, 7, math.sqrt(G * sun_mass / 240), (205, 92, 92)),
            ("Jupiter", 320, 50.0, 25, math.sqrt(G * sun_mass / 320), (255, 165, 79)),
            ("Saturn", 400, 40.0, 20, math.sqrt(G * sun_mass / 400), (250, 230, 144)),
            ("Uranus", 500, 30.0, 15, math.sqrt(G * sun_mass / 500), (64, 224, 208)),
            ("Neptune", 600, 32.0, 13, math.sqrt(G * sun_mass / 600), (30, 144, 255))
        ]
        
        for name, distance, mass, radius, velocity, color in planets_data:
            planet = CelestialBody(
                mass=mass,
                position=np.array([distance, 0.0], dtype=np.float64),
                velocity=np.array([0.0, velocity], dtype=np.float64),
                radius=radius,
                color=color,
                name=name
            )
            bodies.append(planet)
            

        
        return bodies
        
    @staticmethod
    def create_galaxy_collision() -> List[CelestialBody]:
        """Create two colliding galaxy clusters"""
        bodies = []
        
        # Galaxy 1 parameters
        galaxy1_center = np.array([-200, 0], dtype=np.float64)
        galaxy1_velocity = np.array([0.5, 0], dtype=np.float64)
        galaxy1_rotation = 0.02
        
        # Galaxy 2 parameters
        galaxy2_center = np.array([200, 0], dtype=np.float64)
        galaxy2_velocity = np.array([-0.5, 0], dtype=np.float64)
        galaxy2_rotation = -0.02
        
        # Central black holes
        bh1 = CelestialBody(
            mass=500.0,  # Constant mass
            position=galaxy1_center.copy(),
            velocity=galaxy1_velocity.copy(),
            radius=20,
            color=(50, 50, 50),
            name="Black Hole 1"
        )
        bodies.append(bh1)
        
        bh2 = CelestialBody(
            mass=500.0,
            position=galaxy2_center.copy(),
            velocity=galaxy2_velocity.copy(),
            radius=20,
            color=(30, 30, 30),
            name="Black Hole 2"
        )
        bodies.append(bh2)
        
        # Generate stars for each galaxy
        for galaxy_id, (center, base_velocity, rotation, color_base) in enumerate([
            (galaxy1_center, galaxy1_velocity, galaxy1_rotation, (100, 100, 255)),
            (galaxy2_center, galaxy2_velocity, galaxy2_rotation, (255, 100, 100))
        ]):
            for i in range(25):  # 25 stars per galaxy
                # Random position in spiral pattern
                angle = np.random.uniform(0, 2 * np.pi)
                radius = np.random.uniform(20, 150)
                
                # Spiral arm pattern
                spiral_angle = angle + radius * 0.02
                x = center[0] + radius * np.cos(spiral_angle)
                y = center[1] + radius * np.sin(spiral_angle)
                
                # Orbital velocity around galactic center
                orbital_speed = rotation * radius
                vel_x = base_velocity[0] - orbital_speed * np.sin(spiral_angle)
                vel_y = base_velocity[1] + orbital_speed * np.cos(spiral_angle)
                
                # Constant star properties
                mass = 25.0  # Fixed mass for all stars
                star_radius = 8.0  # Fixed radius
                
                # Color variation
                color_variation = np.random.randint(-30, 31)
                star_color = tuple(
                    max(50, min(255, base_color + color_variation)) 
                    for base_color in color_base
                )
                
                star = CelestialBody(
                    mass=mass,
                    position=np.array([x, y], dtype=np.float64),
                    velocity=np.array([vel_x, vel_y], dtype=np.float64),
                    radius=star_radius,
                    color=star_color,
                    name=f"Star G{galaxy_id+1}-{i+1}"
                )
                bodies.append(star)
                
        return bodies
        
    @staticmethod
    def create_asteroid_impact() -> List[CelestialBody]:
        """Create an asteroid impact scenario"""
        bodies = []
        
        # Target planet (Earth-like)
        planet = CelestialBody(
            mass=100.0,  # Constant mass
            position=np.array([0, 0], dtype=np.float64),
            velocity=np.array([0, 0], dtype=np.float64),
            radius=25,
            color=COLORS['planet'],
            name="Planet"
        )
        bodies.append(planet)
        
        # Large asteroid approaching
        asteroid = CelestialBody(
            mass=50.0,  # Constant mass
            position=np.array([-300, -100], dtype=np.float64),
            velocity=np.array([8, 3], dtype=np.float64),  # Constant velocity
            radius=12,
            color=COLORS['asteroid'],
            name="Asteroid"
        )
        bodies.append(asteroid)
        
        # Debris field around the planet
        for i in range(15):
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(40, 80)
            
            debris_x = planet.position[0] + distance * np.cos(angle)
            debris_y = planet.position[1] + distance * np.sin(angle)
            
            # Orbital velocity
            orbital_speed = np.sqrt(6.67430e-11 * planet.mass / (distance * 1000))
            vel_x = -orbital_speed * np.sin(angle) * 0.001  # Scale down
            vel_y = orbital_speed * np.cos(angle) * 0.001
            
            debris = CelestialBody(
                mass=2.0,  # Constant small mass
                position=np.array([debris_x, debris_y], dtype=np.float64),
                velocity=np.array([vel_x * 0.1, vel_y * 0.1], dtype=np.float64),  # Slower constant velocities
                radius=5.0,  # Constant radius
                color=(
                    np.random.randint(100, 200),
                    np.random.randint(80, 150),
                    np.random.randint(50, 120)
                ),
                name=f"Debris-{i+1}"
            )
            bodies.append(debris)
            
        # Add some distant objects for context
        for i in range(5):
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(200, 400)
            
            obj_x = distance * np.cos(angle)
            obj_y = distance * np.sin(angle)
            
            distant_object = CelestialBody(
                mass=15.0,  # Constant mass
                position=np.array([obj_x, obj_y], dtype=np.float64),
                velocity=np.array([0.5, 0.5], dtype=np.float64),  # Constant low velocity
                radius=10.0,  # Constant radius
                color=(
                    np.random.randint(150, 255),
                    np.random.randint(150, 255),
                    np.random.randint(150, 255)
                ),
                name=f"Object-{i+1}"
            )
            bodies.append(distant_object)
            
        return bodies
        
    @staticmethod
    def create_binary_system() -> List[CelestialBody]:
        """Create a binary star system with planets"""
        bodies = []
        
        # Binary stars - simple constant values
        star1_mass = 150.0
        star2_mass = 120.0
        total_mass = star1_mass + star2_mass
        separation = 100
        orbital_velocity = 2.0  # Constant orbital velocity
        
        star1 = CelestialBody(
            mass=star1_mass,
            position=np.array([-separation * star2_mass / total_mass, 0], dtype=np.float64),
            velocity=np.array([0, orbital_velocity * star2_mass / total_mass], dtype=np.float64),
            radius=25,
            color=(255, 200, 100),
            name="Star A"
        )
        bodies.append(star1)
        
        star2 = CelestialBody(
            mass=star2_mass,
            position=np.array([separation * star1_mass / total_mass, 0], dtype=np.float64),
            velocity=np.array([0, -orbital_velocity * star1_mass / total_mass], dtype=np.float64),
            radius=22,
            color=(255, 150, 150),
            name="Star B"
        )
        bodies.append(star2)
        
        # Circumbinary planets
        for i, (distance, mass, radius, name) in enumerate([
            (200, 30.0, 12, "Planet I"),
            (280, 40.0, 15, "Planet II"),
            (380, 25.0, 10, "Planet III")
        ]):
            planet_velocity = 1.5 - (i * 0.3)  # Decreasing constant velocity
            
            planet = CelestialBody(
                mass=mass,
                position=np.array([distance, 0], dtype=np.float64),
                velocity=np.array([0, planet_velocity], dtype=np.float64),
                radius=radius,
                color=COLORS['planet'],
                name=name
            )
            bodies.append(planet)
            
        return bodies
        
    @staticmethod
    def create_three_body_problem() -> List[CelestialBody]:
        """Create a chaotic three-body system"""
        bodies = []
        
        # Three equal mass bodies with constant values
        mass = 100.0
        
        body1 = CelestialBody(
            mass=mass,
            position=np.array([-50, 0], dtype=np.float64),
            velocity=np.array([0, 2], dtype=np.float64),
            radius=20,
            color=(255, 100, 100),
            name="Body 1"
        )
        bodies.append(body1)
        
        body2 = CelestialBody(
            mass=mass,
            position=np.array([50, 0], dtype=np.float64),
            velocity=np.array([0, 2], dtype=np.float64),
            radius=20,
            color=(100, 255, 100),
            name="Body 2"
        )
        bodies.append(body2)
        
        body3 = CelestialBody(
            mass=mass,
            position=np.array([0, 50], dtype=np.float64),
            velocity=np.array([0, -4], dtype=np.float64),
            radius=20,
            color=(100, 100, 255),
            name="Body 3"
        )
        bodies.append(body3)
        
        return bodies
        
    @staticmethod
    def get_all_scenarios() -> dict:
        """Get dictionary of all available scenarios"""
        return {
            "Solar System": ScenarioManager.create_solar_system,
            "Galaxy Collision": ScenarioManager.create_galaxy_collision,
            "Asteroid Impact": ScenarioManager.create_asteroid_impact,
            "Binary System": ScenarioManager.create_binary_system,
            "Three Body Problem": ScenarioManager.create_three_body_problem
        }