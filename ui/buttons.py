"""
UI button components for actions and scenario selection
"""
import pygame
from typing import Callable, Optional, List
from config import *


class Button:
    """Interactive button component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable[[], None]] = None,
        enabled: bool = True
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.enabled = enabled
        
        # Visual properties
        self.bg_color = (70, 70, 80)
        self.bg_hover_color = (90, 90, 100)
        self.bg_pressed_color = (50, 50, 60)
        self.bg_disabled_color = (40, 40, 50)
        self.text_color = UI_TEXT_COLOR
        self.text_disabled_color = (100, 100, 100)
        self.border_color = (120, 120, 140)
        self.border_hover_color = (150, 150, 170)
        
        # Interaction state
        self.pressed = False
        self.hover = False
        
        # Font
        self.font = pygame.font.Font(None, 24)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events, return True if event was consumed"""
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos) and self.callback:
                    self.callback()
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            old_hover = self.hover
            self.hover = self.rect.collidepoint(event.pos)
            if old_hover != self.hover:
                return True
                
        return False
        
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button"""
        self.enabled = enabled
        if not enabled:
            self.pressed = False
            self.hover = False
            
    def set_text(self, text: str) -> None:
        """Set button text"""
        self.text = text
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button"""
        # Determine colors based on state
        if not self.enabled:
            bg_color = self.bg_disabled_color
            text_color = self.text_disabled_color
            border_color = self.border_color
        elif self.pressed:
            bg_color = self.bg_pressed_color
            text_color = self.text_color
            border_color = self.border_hover_color
        elif self.hover:
            bg_color = self.bg_hover_color
            text_color = self.text_color
            border_color = self.border_hover_color
        else:
            bg_color = self.bg_color
            text_color = self.text_color
            border_color = self.border_color
            
        # Draw button background
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class ToggleButton(Button):
    """Button that can be toggled on/off"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable[[bool], None]] = None,
        initial_state: bool = False
    ):
        super().__init__(x, y, width, height, text, None)
        self.toggle_callback = callback
        self.toggled = initial_state
        
        # Override callback to handle toggle
        self.callback = self._toggle
        
        # Additional colors for toggled state
        self.bg_toggled_color = (100, 150, 100)
        self.bg_toggled_hover_color = (120, 170, 120)
        
    def _toggle(self) -> None:
        """Internal toggle handler"""
        self.toggled = not self.toggled
        if self.toggle_callback:
            self.toggle_callback(self.toggled)
            
    def set_toggled(self, toggled: bool) -> None:
        """Set toggle state without triggering callback"""
        self.toggled = toggled
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the toggle button with appropriate colors"""
        # Override colors for toggled state
        if self.toggled and self.enabled:
            if self.hover:
                bg_color = self.bg_toggled_hover_color
            else:
                bg_color = self.bg_toggled_color
            border_color = self.border_hover_color
        else:
            # Use parent class logic
            super().draw(screen)
            return
            
        # Draw button background
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class ButtonPanel:
    """Panel containing multiple buttons"""
    
    def __init__(self, x: int, y: int, width: int, title: str = "Controls"):
        self.x = x
        self.y = y
        self.width = width
        self.title = title
        self.buttons: List[Button] = []
        
        # Visual properties
        self.background_color = (40, 40, 50, 180)
        self.border_color = (100, 100, 120)
        self.title_color = UI_TEXT_COLOR
        
        self.font = pygame.font.Font(None, 24)
        
    def add_button(self, button: Button) -> None:
        """Add a button to the panel"""
        # Position button relative to panel
        buttons_per_row = max(1, self.width // (BUTTON_WIDTH + 10))
        row = len(self.buttons) // buttons_per_row
        col = len(self.buttons) % buttons_per_row
        
        button_x = self.x + 10 + col * (BUTTON_WIDTH + 10)
        button_y = self.y + 40 + row * (BUTTON_HEIGHT + 10)
        
        button.rect.x = button_x
        button.rect.y = button_y
        button.rect.width = BUTTON_WIDTH
        button.rect.height = BUTTON_HEIGHT
        
        self.buttons.append(button)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all buttons"""
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the panel and all buttons"""
        if not self.buttons:
            return
            
        # Calculate panel height
        buttons_per_row = max(1, self.width // (BUTTON_WIDTH + 10))
        rows = (len(self.buttons) + buttons_per_row - 1) // buttons_per_row
        panel_height = 50 + rows * (BUTTON_HEIGHT + 10)
        
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
        
        # Draw all buttons
        for button in self.buttons:
            button.draw(screen)
            
    def get_height(self) -> int:
        """Get the total height of the panel"""
        if not self.buttons:
            return 0
        buttons_per_row = max(1, self.width // (BUTTON_WIDTH + 10))
        rows = (len(self.buttons) + buttons_per_row - 1) // buttons_per_row
        return 50 + rows * (BUTTON_HEIGHT + 10)
        
    def clear_buttons(self) -> None:
        """Remove all buttons from the panel"""
        self.buttons.clear()
        
    def set_title(self, title: str) -> None:
        """Set the panel title"""
        self.title = title


class ScenarioSelector:
    """Dropdown-style selector for cosmic scenarios"""
    
    def __init__(self, x: int, y: int, width: int, scenarios: dict):
        self.x = x
        self.y = y
        self.width = width
        self.height = 30
        self.scenarios = scenarios
        self.selected_scenario = list(scenarios.keys())[0] if scenarios else ""
        self.expanded = False
        
        # Visual properties
        self.bg_color = (60, 60, 70)
        self.bg_hover_color = (80, 80, 90)
        self.text_color = UI_TEXT_COLOR
        self.border_color = (100, 100, 120)
        
        # Font
        self.font = pygame.font.Font(None, 22)
        
        # Callback
        self.callback: Optional[Callable[[str], None]] = None
        
    def set_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for scenario selection"""
        self.callback = callback
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if main_rect.collidepoint(event.pos):
                    self.expanded = not self.expanded
                    return True
                elif self.expanded:
                    # Check if dropdown would extend beyond screen bottom
                    dropdown_height = len(self.scenarios) * self.height
                    # Assume screen height of 800 for calculation
                    expand_upward = (self.y + self.height + dropdown_height) > 800
                    
                    # Check if clicking on an option
                    for i, scenario_name in enumerate(self.scenarios.keys()):
                        if expand_upward:
                            # Options expand upward
                            option_y = self.y - (len(self.scenarios) - i) * self.height
                        else:
                            # Options expand downward (original)
                            option_y = self.y + self.height + i * self.height
                            
                        option_rect = pygame.Rect(
                            self.x, 
                            option_y,
                            self.width, 
                            self.height
                        )
                        if option_rect.collidepoint(event.pos):
                            self.selected_scenario = scenario_name
                            self.expanded = False
                            if self.callback:
                                self.callback(scenario_name)
                            return True
                    # Clicked outside, collapse
                    self.expanded = False
                    
        return False
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scenario selector"""
        main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Draw main selector
        pygame.draw.rect(screen, self.bg_color, main_rect)
        pygame.draw.rect(screen, self.border_color, main_rect, 2)
        
        # Draw selected scenario text
        text_surface = self.font.render(self.selected_scenario, True, self.text_color)
        text_rect = text_surface.get_rect()
        text_rect.centery = main_rect.centery
        text_rect.x = main_rect.x + 10
        screen.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.x + self.width - 15, self.y + 10),
            (self.x + self.width - 25, self.y + 10),
            (self.x + self.width - 20, self.y + 20)
        ]
        pygame.draw.polygon(screen, self.text_color, arrow_points)
        
        # Draw dropdown options if expanded
        if self.expanded:
            # Check if dropdown would extend beyond screen bottom
            dropdown_height = len(self.scenarios) * self.height
            screen_height = screen.get_height()
            expand_upward = (self.y + self.height + dropdown_height) > screen_height
            
            for i, scenario_name in enumerate(self.scenarios.keys()):
                if expand_upward:
                    # Expand upward from the main selector
                    option_y = self.y - (len(self.scenarios) - i) * self.height
                else:
                    # Expand downward (original behavior)
                    option_y = self.y + self.height + i * self.height
                    
                option_rect = pygame.Rect(
                    self.x,
                    option_y,
                    self.width,
                    self.height
                )
                
                # Highlight if hovering
                mouse_pos = pygame.mouse.get_pos()
                hover = option_rect.collidepoint(mouse_pos)
                bg_color = self.bg_hover_color if hover else self.bg_color
                
                pygame.draw.rect(screen, bg_color, option_rect)
                pygame.draw.rect(screen, self.border_color, option_rect, 1)
                
                # Draw option text
                option_text = self.font.render(scenario_name, True, self.text_color)
                option_text_rect = option_text.get_rect()
                option_text_rect.centery = option_rect.centery
                option_text_rect.x = option_rect.x + 10
                screen.blit(option_text, option_text_rect)
                
    def get_total_height(self) -> int:
        """Get total height including expanded options"""
        if self.expanded:
            return self.height + len(self.scenarios) * self.height
        return self.height