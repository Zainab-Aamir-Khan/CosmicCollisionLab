"""
Body Information Panel - displays details about selected celestial bodies
"""
import pygame
import numpy as np
from typing import Optional
from physics.body import CelestialBody


class BodyInfoPanel:
    """Panel to display information about a selected celestial body"""
    
    def __init__(self, x: int, y: int, width: int = 300, height: int = 330):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected_body: Optional[CelestialBody] = None
        
        # Fonts
        self.font_title = pygame.font.Font(None, 24)
        self.font_text = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.border_color = (100, 100, 150)
        self.title_color = (255, 255, 100)
        self.text_color = (200, 200, 200)
        self.value_color = (150, 255, 150)
        
        # Body information database
        self.body_info = {
            "Sun": {
                "type": "G-type Main Sequence Star",
                "description": "The Sun is the star at the center of our Solar System.",
                "facts": [
                    "Surface temperature: ~5,778 K",
                    "Age: ~4.6 billion years",
                    "Composition: ~73% hydrogen, ~25% helium"
                ]
            },
            "Mercury": {
                "type": "Terrestrial Planet",
                "description": "The smallest planet and closest to the Sun.",
                "facts": [
                    "Day length: 59 Earth days",
                    "Year length: 88 Earth days",
                    "Temperature range: -173°C to 427°C"
                ]
            },
            "Venus": {
                "type": "Terrestrial Planet", 
                "description": "The hottest planet due to extreme greenhouse effect.",
                "facts": [
                    "Surface temperature: 462°C",
                    "Thick CO2 atmosphere",
                    "Rotates backwards (retrograde)"
                ]
            },
            "Earth": {
                "type": "Terrestrial Planet",
                "description": "The only known planet with life.",
                "facts": [
                    "71% surface covered by water",
                    "Nitrogen-oxygen atmosphere",
                    "One natural satellite (Moon)"
                ]
            },
            "Mars": {
                "type": "Terrestrial Planet",
                "description": "The 'Red Planet' with polar ice caps.",
                "facts": [
                    "Day length: 24h 37m (similar to Earth)",
                    "Has the largest volcano: Olympus Mons",
                    "Two small moons: Phobos and Deimos"
                ]
            },
            "Jupiter": {
                "type": "Gas Giant",
                "description": "The largest planet with a Great Red Spot storm.",
                "facts": [
                    "Has over 79 known moons",
                    "Could fit 1,300 Earths inside it",
                    "Great Red Spot is larger than Earth"
                ]
            },
            "Saturn": {
                "type": "Gas Giant",
                "description": "Famous for its spectacular ring system.",
                "facts": [
                    "Density less than water",
                    "Has over 80 known moons",
                    "Rings made of ice and rock particles"
                ]
            },
            "Uranus": {
                "type": "Ice Giant",
                "description": "Tilted on its side with faint rings.",
                "facts": [
                    "Rotates on its side (98° tilt)",
                    "Made mostly of water, methane, and ammonia",
                    "Has 27 known moons"
                ]
            },
            "Neptune": {
                "type": "Ice Giant",
                "description": "The windiest planet in the solar system.",
                "facts": [
                    "Wind speeds up to 2,100 km/h",
                    "Takes 165 Earth years to orbit the Sun",
                    "Has 14 known moons, including Triton"
                ]
            }
        }
    
    def set_selected_body(self, body: Optional[CelestialBody]) -> None:
        """Set the currently selected body"""
        self.selected_body = body
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the information panel"""
        if not self.selected_body:
            return
            
        # Draw background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect)
        pygame.draw.rect(screen, self.border_color, panel_rect, 2)
        
        # Draw title
        title_text = f"📍 {self.selected_body.name}"
        title_surface = self.font_title.render(title_text, True, self.title_color)
        screen.blit(title_surface, (self.x + 10, self.y + 10))
        
        y_offset = 45
        
        # Get body info
        info = self.body_info.get(self.selected_body.name, {})
        
        # Draw type
        if "type" in info:
            type_text = f"Type: {info['type']}"
            type_surface = self.font_text.render(type_text, True, self.value_color)
            screen.blit(type_surface, (self.x + 10, self.y + y_offset))
            y_offset += 25
        
        # Draw description
        if "description" in info:
            desc_lines = self._wrap_text(info['description'], self.width - 20)
            for line in desc_lines:
                desc_surface = self.font_small.render(line, True, self.text_color)
                screen.blit(desc_surface, (self.x + 10, self.y + y_offset))
                y_offset += 18
            y_offset += 10
        
        # Draw physical properties
        y_offset = self._draw_physical_properties(screen, y_offset)
        
        # Draw interesting facts
        if "facts" in info and y_offset < self.y + self.height - 60:
            facts_title = self.font_text.render("Interesting Facts:", True, self.title_color)
            screen.blit(facts_title, (self.x + 10, self.y + y_offset))
            y_offset += 25
            
            for fact in info['facts'][:3]:  # Limit to 3 facts to fit
                if y_offset < self.y + self.height - 20:
                    fact_lines = self._wrap_text(f"• {fact}", self.width - 20)
                    for line in fact_lines:
                        fact_surface = self.font_small.render(line, True, self.text_color)
                        screen.blit(fact_surface, (self.x + 10, self.y + y_offset))
                        y_offset += 16
    
    def _draw_physical_properties(self, screen: pygame.Surface, y_offset: int) -> int:
        """Draw physical properties of the selected body"""
        if not self.selected_body:
            return y_offset
            
        # Properties title
        props_title = self.font_text.render("Physical Properties:", True, self.title_color)
        screen.blit(props_title, (self.x + 10, self.y + y_offset))
        y_offset += 25
        
        # Mass
        mass_text = f"Mass: {self.selected_body.mass:.1f} units"
        mass_surface = self.font_small.render(mass_text, True, self.text_color)
        screen.blit(mass_surface, (self.x + 10, self.y + y_offset))
        y_offset += 18
        
        # Radius  
        radius_text = f"Radius: {self.selected_body.radius:.1f} pixels"
        radius_surface = self.font_small.render(radius_text, True, self.text_color)
        screen.blit(radius_surface, (self.x + 10, self.y + y_offset))
        y_offset += 18
        
        # Velocity
        velocity = np.linalg.norm(self.selected_body.velocity)
        velocity_text = f"Velocity: {velocity:.2f} units/s"
        velocity_surface = self.font_small.render(velocity_text, True, self.text_color)
        screen.blit(velocity_surface, (self.x + 10, self.y + y_offset))
        y_offset += 18
        
        # Distance from origin (for planets, distance from Sun)
        distance = np.linalg.norm(self.selected_body.position)
        if self.selected_body.name != "Sun":
            distance_text = f"Distance from Sun: {distance:.1f} units"
        else:
            distance_text = f"Position: Center of Solar System"
        distance_surface = self.font_small.render(distance_text, True, self.text_color)
        screen.blit(distance_surface, (self.x + 10, self.y + y_offset))
        y_offset += 25
        
        return y_offset
    
    def _wrap_text(self, text: str, max_width: int) -> list:
        """Wrap text to fit within the specified width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_surface = self.font_small.render(test_line, True, self.text_color)
            
            if text_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
            
        return lines