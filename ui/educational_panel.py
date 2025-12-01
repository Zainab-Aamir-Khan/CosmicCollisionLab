"""Educational information panel for the Cosmic Collision Lab"""

import pygame
from typing import Dict, List, Optional
import numpy as np


class EducationalPanel:
    """Display educational information about physics and astronomy"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 28)
        self.font_text = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Educational content for different scenarios
        self.scenario_info = {
            "Solar System": {
                "title": "Solar System Dynamics",
                "facts": [
                    "The Sun contains 99.86% of the system's mass",
                    "Planets orbit in elliptical paths (Kepler's Laws)",
                    "Gravitational force decreases with distance²",
                    "Orbital velocity = √(GM/r)"
                ]
            },
            "Galaxy Collision": {
                "title": "Galactic Mergers",
                "facts": [
                    "Galaxy collisions take millions of years",
                    "Stars rarely collide due to vast distances",
                    "Dark matter halos interact gravitationally",
                    "Can trigger new star formation"
                ]
            },
            "Asteroid Impact": {
                "title": "Impact Physics",
                "facts": [
                    "KE = ½mv² - kinetic energy increases with v²",
                    "Momentum is conserved in collisions",
                    "Impact craters depend on velocity and mass",
                    "Real asteroids travel 20-70 km/s"
                ]
            },
            "Binary System": {
                "title": "Binary Star Systems",
                "facts": [
                    "Stars orbit their common center of mass",
                    "Period depends on mass and separation",
                    "Most stars exist in binary/multiple systems",
                    "Orbital energy is conserved"
                ]
            },
            "Three-Body Problem": {
                "title": "Chaotic Dynamics",
                "facts": [
                    "No general analytical solution exists",
                    "Extremely sensitive to initial conditions",
                    "Small changes lead to vastly different outcomes",
                    "Used to study stability in astronomy"
                ]
            }
        }
        
        # Physics formulas
        self.formulas = {
            "Gravity": "F = G × (m₁ × m₂) / r²",
            "Acceleration": "a = F / m",
            "Velocity": "v = v₀ + a × Δt",
            "Kinetic Energy": "KE = ½ × m × v²"
        }
        
    def draw(self, screen: pygame.Surface, scenario_name: str, 
             physics_stats: Optional[Dict] = None) -> None:
        """Draw the educational information panel"""
        # Panel dimensions
        panel_width = 380
        panel_height = 320
        panel_x = self.width - panel_width - 10
        panel_y = 10
        
        # Create semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill((15, 25, 45))
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw border
        pygame.draw.rect(screen, (100, 150, 255), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw content
        y_offset = panel_y + 15
        x_offset = panel_x + 15
        
        # Main title
        title_text = self.font_title.render("Physics & Astronomy", True, (100, 200, 255))
        screen.blit(title_text, (x_offset, y_offset))
        y_offset += 35
        
        # Scenario-specific information
        scenario_data = self.scenario_info.get(scenario_name, {
            "title": "Simulation",
            "facts": ["Explore gravitational physics!", "Drag bodies to move them", 
                     "Scroll to zoom in/out", "Press H for help"]
        })
        
        # Scenario title
        scenario_title = self.font_text.render(scenario_data["title"], True, (255, 255, 100))
        screen.blit(scenario_title, (x_offset, y_offset))
        y_offset += 30
        
        # Draw facts
        for fact in scenario_data["facts"]:
            # Word wrap for long facts
            words = fact.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if self.font_small.size(test_line)[0] < panel_width - 35:
                    line = test_line
                else:
                    if line:
                        fact_text = self.font_small.render("• " + line, True, (220, 220, 220))
                        screen.blit(fact_text, (x_offset + 5, y_offset))
                        y_offset += 22
                    line = word + " "
            if line:
                fact_text = self.font_small.render("• " + line, True, (220, 220, 220))
                screen.blit(fact_text, (x_offset + 5, y_offset))
                y_offset += 22
        
        y_offset += 10
        
        # Draw physics stats if available
        if physics_stats:
            stats_title = self.font_text.render("Current Physics", True, (100, 255, 150))
            screen.blit(stats_title, (x_offset, y_offset))
            y_offset += 25
            
            if 'total_energy' in physics_stats:
                energy_text = self.font_small.render(
                    f"Total Energy: {physics_stats['total_energy']:.2e}", 
                    True, (200, 200, 200))
                screen.blit(energy_text, (x_offset + 5, y_offset))
                y_offset += 20
                
            if 'momentum' in physics_stats:
                momentum = physics_stats['momentum']
                momentum_mag = np.linalg.norm(momentum)
                momentum_text = self.font_small.render(
                    f"Momentum: {momentum_mag:.2e}", 
                    True, (200, 200, 200))
                screen.blit(momentum_text, (x_offset + 5, y_offset))
                y_offset += 20
        
        # Draw formula reference at bottom
        formula_y = panel_y + panel_height - 55
        formula_title = self.font_small.render("Key Formula:", True, (255, 200, 100))
        screen.blit(formula_title, (x_offset, formula_y))
        formula_y += 20
        
        formula_text = self.font_small.render(self.formulas["Gravity"], True, (200, 200, 200))
        screen.blit(formula_text, (x_offset + 5, formula_y))


class WelcomeScreen:
    """Display welcome screen for the application"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_text = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the welcome screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(240)
        overlay.fill((10, 15, 30))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.font_title.render("COSMIC COLLISION LAB", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 120))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_subtitle.render("Interactive Astrophysics Simulator", True, (150, 220, 255))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 180))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Version info
        version_text = self.font_text.render("Final Year Project 2025 | Version 1.0.0", True, (200, 200, 200))
        version_rect = version_text.get_rect(center=(self.width // 2, 220))
        screen.blit(version_text, version_rect)
        
        # Features
        y_offset = 280
        features = [
            " Real-time Newtonian Gravity Simulation",
            " Interactive Drag-and-Drop Celestial Bodies",
            " Multiple Cosmic Scenarios (Solar System, Galaxies, Asteroids)",
            " Physics Statistics & Educational Information",
            " Orbit Trails, Zoom, Pan, and Smooth Camera Controls"
        ]
        
        for feature in features:
            feature_text = self.font_text.render(feature, True, (220, 240, 255))
            feature_rect = feature_text.get_rect(center=(self.width // 2, y_offset))
            screen.blit(feature_text, feature_rect)
            y_offset += 40
        
        # Instructions
        y_offset += 30
        instructions = [
            "Quick Start Guide:",
            "• Select a scenario from the dropdown menu",
            "• Left-click and drag to move celestial bodies",
            "• Right-click and drag to pan the camera view",
            "• Use mouse wheel to zoom in and out",
            "• Press SPACE to pause/resume the simulation",
            "• Press H for detailed help and controls"
        ]
        
        for i, instruction in enumerate(instructions):
            color = (255, 255, 150) if i == 0 else (200, 200, 200)
            font = self.font_text if i == 0 else self.font_small
            instruction_text = font.render(instruction, True, color)
            instruction_rect = instruction_text.get_rect(center=(self.width // 2, y_offset))
            screen.blit(instruction_text, instruction_rect)
            y_offset += 25 if i == 0 else 22
        
        # Future Works button (bottom left)
        future_button_text = self.font_text.render(" Future Works (U)", True, (255, 255, 255))
        future_button_rect = pygame.Rect(20, self.height - 80, 200, 40)
        
        # Button background
        button_surface = pygame.Surface((200, 40))
        button_surface.set_alpha(180)
        button_surface.fill((70, 70, 80))
        screen.blit(button_surface, (20, self.height - 80))
        
        # Button border
        pygame.draw.rect(screen, (120, 120, 140), future_button_rect, 2)
        
        # Button text
        text_rect = future_button_text.get_rect(center=future_button_rect.center)
        screen.blit(future_button_text, text_rect)
        
        # Continue prompt
        y_offset = self.height - 60
        continue_text = self.font_subtitle.render("Press W to Start", True, (100, 255, 150))
        continue_rect = continue_text.get_rect(center=(self.width // 2, y_offset))
        screen.blit(continue_text, continue_rect)
        
        # Blink effect for continue prompt
        import time
        if int(time.time() * 2) % 2 == 0:
            arrow_text = self.font_title.render("▼", True, (100, 255, 150))
            arrow_rect = arrow_text.get_rect(center=(self.width // 2, y_offset + 35))
            screen.blit(arrow_text, arrow_rect)
