"""
UI slider components for parameter adjustment
"""
import pygame
from typing import Callable, Optional
import math
from config import *


class Slider:
    """Interactive slider for adjusting numeric values"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_value: float,
        max_value: float,
        initial_value: float,
        label: str = "",
        callback: Optional[Callable[[float], None]] = None,
        logarithmic: bool = False
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.callback = callback
        self.logarithmic = logarithmic
        
        # Visual properties
        self.bg_color = (60, 60, 70)
        self.fg_color = (100, 150, 200)
        self.handle_color = (200, 200, 220)
        self.text_color = UI_TEXT_COLOR
        self.border_color = (100, 100, 120)
        
        # Interaction state
        self.dragging = False
        self.hover = False
        
        # Font
        self.font = pygame.font.Font(None, 20)
        
        # Calculate initial handle position
        self._update_handle_position()
        
    def _update_handle_position(self) -> None:
        """Update handle position based on current value"""
        if self.logarithmic:
            if self.min_value <= 0:
                raise ValueError("Logarithmic slider requires positive min_value")
            log_min = math.log10(self.min_value)
            log_max = math.log10(self.max_value)
            log_value = math.log10(self.value)
            ratio = (log_value - log_min) / (log_max - log_min)
        else:
            ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
            
        ratio = max(0, min(1, ratio))
        self.handle_x = self.rect.x + int(ratio * self.rect.width)
        
    def _value_from_position(self, x: int) -> float:
        """Calculate value from handle position"""
        ratio = max(0, min(1, (x - self.rect.x) / self.rect.width))
        
        if self.logarithmic:
            log_min = math.log10(self.min_value)
            log_max = math.log10(self.max_value)
            log_value = log_min + ratio * (log_max - log_min)
            return 10 ** log_value
        else:
            return self.min_value + ratio * (self.max_value - self.min_value)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events, return True if event was consumed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self.set_value_from_position(event.pos[0])
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            
            if self.dragging:
                self.set_value_from_position(event.pos[0])
                return True
                
        return False
        
    def set_value_from_position(self, x: int) -> None:
        """Set value from mouse position"""
        new_value = self._value_from_position(x)
        self.set_value(new_value)
        
    def set_value(self, value: float) -> None:
        """Set the slider value"""
        old_value = self.value
        self.value = max(self.min_value, min(self.max_value, value))
        self._update_handle_position()
        
        # Call callback if value changed
        if self.callback and abs(self.value - old_value) > 1e-10:
            self.callback(self.value)
            
    def get_value(self) -> float:
        """Get the current slider value"""
        return self.value
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the slider"""
        # Draw slider track
        track_color = self.border_color if self.hover else self.bg_color
        pygame.draw.rect(screen, track_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Draw filled portion
        fill_width = self.handle_x - self.rect.x
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(screen, self.fg_color, fill_rect)
            
        # Draw handle
        handle_rect = pygame.Rect(
            self.handle_x - 5, 
            self.rect.y - 2, 
            10, 
            self.rect.height + 4
        )
        pygame.draw.rect(screen, self.handle_color, handle_rect)
        pygame.draw.rect(screen, self.border_color, handle_rect, 2)
        
        # Draw label and value
        if self.label:
            label_text = f"{self.label}: {self._format_value()}"
            text_surface = self.font.render(label_text, True, self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.bottomleft = (self.rect.x, self.rect.y - 5)
            screen.blit(text_surface, text_rect)
            
    def _format_value(self) -> str:
        """Format value for display"""
        if abs(self.value) >= 1e6 or (abs(self.value) < 1e-3 and self.value != 0):
            return f"{self.value:.2e}"
        elif abs(self.value) < 1:
            return f"{self.value:.4f}"
        else:
            return f"{self.value:.2f}"


class SliderPanel:
    """Panel containing multiple sliders"""
    
    def __init__(self, x: int, y: int, width: int):
        self.x = x
        self.y = y
        self.width = width
        self.sliders = []
        self.background_color = (40, 40, 50, 180)  # Semi-transparent
        self.border_color = (100, 100, 120)
        self.title_color = UI_TEXT_COLOR
        
        self.font = pygame.font.Font(None, 24)
        self.title = "Parameters"
        
    def add_slider(self, slider: Slider) -> None:
        """Add a slider to the panel"""
        # Position slider relative to panel with more spacing from title
        slider_y = self.y + 60 + len(self.sliders) * 50
        slider.rect.x = self.x + 10
        slider.rect.y = slider_y
        slider.rect.width = min(slider.rect.width, self.width - 20)
        slider._update_handle_position()
        
        self.sliders.append(slider)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all sliders"""
        for slider in self.sliders:
            if slider.handle_event(event):
                return True
        return False
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the panel and all sliders"""
        if not self.sliders:
            return
            
        # Calculate panel height with extra spacing
        panel_height = 70 + len(self.sliders) * 50
        
        # Draw panel background
        panel_surface = pygame.Surface((self.width, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill(self.background_color[:3])
        screen.blit(panel_surface, (self.x, self.y))
        
        # Draw panel border
        panel_rect = pygame.Rect(self.x, self.y, self.width, panel_height)
        pygame.draw.rect(screen, self.border_color, panel_rect, 2)
        
        # Draw title
        title_surface = self.font.render(self.title, True, self.title_color)
        title_rect = title_surface.get_rect()
        title_rect.centerx = self.x + self.width // 2
        title_rect.y = self.y + 10
        screen.blit(title_surface, title_rect)
        
        # Draw all sliders
        for slider in self.sliders:
            slider.draw(screen)
            
    def get_height(self) -> int:
        """Get the total height of the panel"""
        return 50 + len(self.sliders) * 50 if self.sliders else 0
        
    def clear_sliders(self) -> None:
        """Remove all sliders from the panel"""
        self.sliders.clear()
        
    def set_title(self, title: str) -> None:
        """Set the panel title"""
        self.title = title