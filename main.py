"""
Cosmic Collision Lab - Interactive 2D Astrophysics Simulator
Main application entry point
"""
import pygame
import sys
import numpy as np
from typing import Optional, Dict, Any
import traceback

# Import simulation components
from physics.physics_engine import PhysicsEngine
from physics.body import CelestialBody
from simulation.renderer import Renderer
from simulation.scenarios import ScenarioManager
from ui.sliders import Slider, SliderPanel
from ui.buttons import Button, ToggleButton, ButtonPanel, ScenarioSelector
from ui.drag_handler import DragHandler, CreationTool
from ui.educational_panel import EducationalPanel, WelcomeScreen
from ui.future_works import FutureWorksPanel
from ui.body_info_panel import BodyInfoPanel
from api.server import APIServer
from config import *


class CosmicCollisionLab:
    """Main application class for the Cosmic Collision Lab"""
    
    # Project Information
    PROJECT_TITLE = "Cosmic Collision Lab"
    PROJECT_VERSION = "1.0.0"
    PROJECT_AUTHORS = "Final Year Project - 2025"
    
    def __init__(self):
        # Initialize core systems
        self.physics_engine = PhysicsEngine(GRAVITY_CONSTANT)
        self.physics_engine.pause()  # Start paused for educational purposes
        self.renderer = Renderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # UI systems
        self.drag_handler = DragHandler(self.physics_engine, self.renderer.camera)
        self.creation_tool = CreationTool(self.physics_engine, self.renderer.camera)
        
        # Educational components
        self.educational_panel = EducationalPanel(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.welcome_screen = WelcomeScreen(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.future_works_panel = FutureWorksPanel(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.body_info_panel = BodyInfoPanel(WINDOW_WIDTH - 320, WINDOW_HEIGHT - 370, width=300, height=330)
        
        # Selected body for UI interaction
        self.selected_body: Optional[CelestialBody] = None
        
        # UI panels
        self._setup_ui()
        
        # API server (disabled by default)
        self.api_server = None
        self.api_enabled = False
        
        # UI state
        self.running = True
        self.show_help = False
        self.show_educational_info = True  # Show by default for educational purposes
        self.show_welcome_screen = True  # Show welcome on first launch
        self.show_future_works = False  # Show future works panel
        self.current_scenario = "Solar System"  # Track current scenario
        
        # Performance tracking
        self.physics_dt = TIME_SCALE
        self.last_update_time = pygame.time.get_ticks()
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Load default scenario
        self._load_scenario("Solar System")
        
        # Debug: Print body positions
        print(f"Loaded {len(self.physics_engine.bodies)} bodies:")
        for body in self.physics_engine.bodies:
            print(f"  {body.name}: position={body.position}, radius={body.radius}")
        
    def _setup_ui(self) -> None:
        """Setup UI panels and controls"""
        # Parameter sliders panel - moved to avoid overlap with simulation info
        self.slider_panel = SliderPanel(10, 240, 250)
        self.slider_panel.set_title("Body Parameters")
        
        # Control buttons panel - wider to accommodate 2 columns of buttons
        self.button_panel = ButtonPanel(10, 470, 270, "Controls")
        
        # Scenario selector
        scenarios = ScenarioManager.get_all_scenarios()
        self.scenario_selector = ScenarioSelector(10, 690, 200, scenarios)
        
        # Add control buttons
        self._setup_control_buttons()
        
    def _setup_control_buttons(self) -> None:
        """Setup control buttons"""
        buttons = [
            Button(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT, "Pause/Resume", self._toggle_pause),
            Button(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT, "Reset", self._reset_simulation),
            Button(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT, "Welcome", self._show_welcome),
            ToggleButton(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT, "Trails", self._toggle_trails, True),
            ToggleButton(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT, "Drag Mode", self._toggle_drag_mode, False),
            ToggleButton(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT, "Add Body", self._toggle_creation_mode, False),
            ToggleButton(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT, "Help", self._toggle_help)
        ]
        
        for button in buttons:
            self.button_panel.add_button(button)
            
    def _setup_callbacks(self) -> None:
        """Setup event callbacks"""
        # Drag handler callbacks
        self.drag_handler.set_selection_callback(self._on_body_selected)
        
        # Scenario selector callback
        self.scenario_selector.set_callback(self._load_scenario)
        
        # Creation tool callback
        self.creation_tool.set_creation_callback(self._on_body_created)
        
    def _on_body_selected(self, body: Optional[CelestialBody]) -> None:
        """Handle body selection changes"""
        self.selected_body = body
        self.body_info_panel.set_selected_body(body)
        self._update_parameter_sliders()
        
    def _on_body_created(self, body: CelestialBody) -> None:
        """Handle new body creation"""
        self.selected_body = body
        self.body_info_panel.set_selected_body(body)
        self._update_parameter_sliders()
        
    def _update_parameter_sliders(self) -> None:
        """Update parameter sliders based on selected body"""
        self.slider_panel.clear_sliders()
        
        if self.selected_body:
            # Mass slider (logarithmic)
            mass_slider = Slider(
                0, 0, SLIDER_WIDTH, SLIDER_HEIGHT,
                MIN_MASS, MAX_MASS, self.selected_body.mass,
                "Mass (kg)", self._on_mass_changed, logarithmic=True
            )
            self.slider_panel.add_slider(mass_slider)
            
            # Radius slider
            radius_slider = Slider(
                0, 0, SLIDER_WIDTH, SLIDER_HEIGHT,
                MIN_RADIUS, MAX_RADIUS, self.selected_body.radius,
                "Radius", self._on_radius_changed
            )
            self.slider_panel.add_slider(radius_slider)
            
            # Velocity magnitude slider
            current_velocity = np.linalg.norm(self.selected_body.velocity)
            velocity_slider = Slider(
                0, 0, SLIDER_WIDTH, SLIDER_HEIGHT,
                0, 50, current_velocity,
                "Velocity", self._on_velocity_changed
            )
            self.slider_panel.add_slider(velocity_slider)
            
    def _on_mass_changed(self, value: float) -> None:
        """Handle mass slider change"""
        if self.selected_body:
            self.selected_body.mass = value
            
    def _on_radius_changed(self, value: float) -> None:
        """Handle radius slider change"""
        if self.selected_body:
            self.selected_body.radius = value
            
    def _on_velocity_changed(self, value: float) -> None:
        """Handle velocity slider change"""
        if self.selected_body:
            current_velocity = self.selected_body.velocity
            current_magnitude = np.linalg.norm(current_velocity)
            
            if current_magnitude > 0:
                # Scale existing velocity
                self.selected_body.velocity = (current_velocity / current_magnitude) * value
            else:
                # Set random direction
                angle = np.random.uniform(0, 2 * np.pi)
                self.selected_body.velocity = np.array([np.cos(angle), np.sin(angle)], dtype=np.float64) * value
                
    def _toggle_pause(self) -> None:
        """Toggle simulation pause state"""
        if self.physics_engine.is_paused():
            self.physics_engine.resume()
        else:
            self.physics_engine.pause()
            
    def _reset_simulation(self) -> None:
        """Reset the simulation to current scenario"""
        # Reload the current scenario
        self._load_scenario(self.current_scenario)
        
    def _toggle_trails(self, enabled: bool) -> None:
        """Toggle trail visibility"""
        for body in self.physics_engine.bodies:
            body.trail_enabled = enabled
        self.renderer.show_trails = enabled
        
    def _toggle_drag_mode(self, enabled: bool) -> None:
        """Toggle drag mode for celestial bodies"""
        self.drag_handler.set_drag_mode_enabled(enabled)
        if enabled:
            print("Drag mode enabled: Click and drag planets to move them")
        else:
            print("Drag mode disabled: Click planets to select and view information")
        
    def _toggle_api(self, enabled: bool) -> None:
        """Toggle API server"""
        if enabled and not self.api_enabled:
            if self.api_server is None:
                from api.server import APIServer
                self.api_server = APIServer(self.physics_engine)
            self.api_server.start_server()
            self.api_enabled = True
        elif not enabled and self.api_enabled and self.api_server:
            self.api_server.stop_server()
            self.api_enabled = False
            
    def _toggle_creation_mode(self, enabled: bool) -> None:
        """Toggle body creation mode"""
        self.creation_tool.set_creation_mode(enabled)
        if enabled:
            print("Add Body mode enabled: Click to place new celestial bodies")
        else:
            print("Add Body mode disabled")
        
    def _toggle_help(self, enabled: bool) -> None:
        """Toggle help display"""
        self.show_help = enabled
        
    def _toggle_educational_info(self) -> None:
        """Toggle educational information panel"""
        self.show_educational_info = not self.show_educational_info
        
    def _show_welcome(self) -> None:
        """Show welcome screen"""
        self.show_welcome_screen = True
        
    def _take_screenshot(self) -> None:
        """Take a screenshot of the current simulation"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cosmic_collision_{timestamp}.png"
        pygame.image.save(self.renderer.screen, filename)
        print(f"Screenshot saved as: {filename}")
        
    def _take_screenshot(self) -> None:
        """Take a screenshot of the current simulation"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cosmic_collision_{timestamp}.png"
        pygame.image.save(self.renderer.screen, filename)
        print(f"Screenshot saved as: {filename}")
        
    def _load_scenario(self, scenario_name: str) -> None:
        """Load a predefined scenario"""
        try:
            scenarios = ScenarioManager.get_all_scenarios()
            if scenario_name in scenarios:
                self.physics_engine.clear_bodies()
                bodies = scenarios[scenario_name]()
                for body in bodies:
                    self.physics_engine.add_body(body)
                    
                # Reset camera to center and appropriate zoom for solar system
                self.renderer.camera.offset = np.array([WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2], dtype=float)
                if scenario_name == "Solar System":
                    self.renderer.camera.zoom = 0.6  # Zoom out for solar system
                else:
                    self.renderer.camera.zoom = 0.8
                
                # Update current scenario
                self.current_scenario = scenario_name
                
                # Clear selection
                self.selected_body = None
                self.body_info_panel.set_selected_body(None)
                self._update_parameter_sliders()
                
        except Exception as e:
            print(f"Error loading scenario '{scenario_name}': {e}")
            traceback.print_exc()
            
    def handle_events(self) -> None:
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key)
                
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_mouse_wheel(event)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.show_welcome_screen:  # Left click on welcome screen
                    # Check if Future Works button was clicked
                    future_button_rect = pygame.Rect(20, WINDOW_HEIGHT - 80, 200, 40)
                    if future_button_rect.collidepoint(event.pos):
                        self.show_future_works = True
                        self.show_welcome_screen = False
                        print("Future works button clicked")
                elif event.button == 3:  # Right mouse button
                    self._start_pan(event.pos)
                    
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[2]:  # Right mouse button held
                    self._update_pan(event.rel)
                    
            elif event.type == pygame.VIDEORESIZE:
                self.renderer.handle_window_resize(event.size)
            
            # Only handle UI events when in simulation mode (not welcome/future works)
            if not self.show_welcome_screen and not self.show_future_works:
                # Let UI components handle events - scenario selector first to handle dropdown clicks
                if not (self.scenario_selector.handle_event(event) or
                       self.slider_panel.handle_event(event) or 
                       self.button_panel.handle_event(event) or
                       self.creation_tool.handle_event(event)):
                    # Only handle drag events if UI didn't consume the event
                    self.drag_handler.handle_event(event)
                
    def _handle_key_press(self, key: int) -> None:
        """Handle keyboard input"""
        if key == pygame.K_SPACE:
            self._toggle_pause()
        elif key == pygame.K_r:
            self._reset_simulation()
        elif key == pygame.K_t:
            self._toggle_trails(not self.renderer.show_trails)
        elif key == pygame.K_i:
            self.renderer.toggle_info()
        elif key == pygame.K_f:
            self.renderer.toggle_fps()
        elif key == pygame.K_h or key == pygame.K_F1:
            self.show_help = not self.show_help
        elif key == pygame.K_e:
            self._toggle_educational_info()
        elif key == pygame.K_w:
            if self.show_welcome_screen:
                self.show_welcome_screen = False
            else:
                self.show_welcome_screen = True  # Return to welcome screen
        elif key == pygame.K_u:  # U for fUtUre works
            if self.show_future_works:
                self.show_future_works = False
                self.show_welcome_screen = True  # Return to welcome screen
                print("Returning to welcome screen")
            else:
                self.show_future_works = True
                self.show_welcome_screen = False  # Hide welcome when showing future works
                print("Future works panel opened")
        elif key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
            self._take_screenshot()
        elif key == pygame.K_ESCAPE:
            if self.selected_body:
                self.selected_body = None
                self.body_info_panel.set_selected_body(None)
                self._update_parameter_sliders()
            else:
                self.running = False
                
    def _handle_mouse_wheel(self, event: pygame.event.Event) -> None:
        """Handle mouse wheel zoom or scrolling"""
        if self.show_future_works:
            # Handle scrolling in future works panel
            self.future_works_panel.handle_scroll(event.y)
        elif not self.show_welcome_screen:
            # Handle camera zoom in simulation mode
            mouse_pos = pygame.mouse.get_pos()
            zoom_factor = 1.1 if event.y > 0 else 1/1.1
            self.renderer.camera.zoom_at(mouse_pos, zoom_factor)
        
    def _start_pan(self, pos) -> None:
        """Start camera panning"""
        pass  # Panning is handled in mouse motion
        
    def _update_pan(self, rel) -> None:
        """Update camera panning"""
        self.renderer.camera.pan(np.array(rel))
        
    def update(self) -> None:
        """Update simulation state"""
        current_time = pygame.time.get_ticks()
        
        # Update physics
        if not self.physics_engine.is_paused():
            self.physics_engine.update(self.physics_dt)
            
        self.last_update_time = current_time
        
    def render(self) -> None:
        """Render the simulation"""
        # Clear screen
        self.renderer.clear_screen()
        
        # Only draw simulation elements when not on welcome/future works screens
        if not self.show_welcome_screen and not self.show_future_works:
            # Draw background stars
            self.renderer.draw_star_field()
            
            # Draw celestial bodies
            self.renderer.draw_bodies(self.physics_engine.bodies)
            
            # Draw drag/selection indicators
            self.drag_handler.draw_selection_indicators(self.renderer.screen, self.selected_body)
        
        # Draw based on current screen state
        if self.show_welcome_screen:
            # Only draw welcome screen - no simulation background
            self.welcome_screen.draw(self.renderer.screen)
        elif self.show_future_works:
            # Only draw future works page - no simulation background
            self.future_works_panel.draw(self.renderer.screen)
        else:
            # Draw full simulation interface
            # Draw collision flash effects
            recent_collisions = self.physics_engine.get_recent_collisions()
            for collision in recent_collisions:
                age = self.physics_engine.time_elapsed - collision['time']
                intensity = collision['intensity'] * max(0, 1 - age / 2.0)  # Fade over 2 seconds
                if intensity > 0:
                    self.renderer.draw_collision_flash(collision['position'], intensity)
            
            # Draw mouse coordinates
            self.renderer.draw_mouse_coordinates()
            
            # Draw UI panels
            self.slider_panel.draw(self.renderer.screen)
            self.button_panel.draw(self.renderer.screen)
            self.scenario_selector.draw(self.renderer.screen)
            self.body_info_panel.draw(self.renderer.screen)
            
            # Draw educational panel
            if self.show_educational_info:
                physics_stats = {
                    'total_energy': self.physics_engine.get_total_energy(),
                    'momentum': self.physics_engine.get_total_momentum()
                }
                self.educational_panel.draw(self.renderer.screen, self.current_scenario, physics_stats)
            
            # Draw simulation info with FPS
            stats = self.physics_engine.get_simulation_stats()
            stats['fps'] = self.renderer.clock.get_fps()  # Add current FPS to stats
            self.renderer.draw_ui_panel(stats, self.selected_body)
        
        # Draw FPS counter only on welcome screen
        if self.show_welcome_screen and self.renderer.show_fps:
            self.renderer.draw_fps_counter()
        
        # Draw help if enabled
        if self.show_help:
            self._draw_help()
            
        # Update display
        self.renderer.update_display()
        
    def _draw_help(self) -> None:
        """Draw help overlay"""
        help_surface = pygame.Surface((400, 300))
        help_surface.set_alpha(220)
        help_surface.fill((20, 20, 30))
        
        help_text = [
            "COSMIC COLLISION LAB - HELP",
            "",
            "Mouse Controls:",
            "  Left Click + Drag: Move bodies",
            "  Right Click + Drag: Pan camera",
            "  Mouse Wheel: Zoom in/out",
            "",
            "Keyboard Shortcuts:",
            "  SPACE: Pause/Resume",
            "  R: Reset simulation",
            "  T: Toggle trails",
            "  I: Toggle info panel",
            "  F: Toggle FPS counter",
            "  E: Toggle educational info",
            "  U: Toggle future works",
            "  W: Return to welcome screen",
            "  Ctrl+S: Take screenshot",
            "  H: Toggle this help",
            "  ESC: Deselect / Exit",
            "",
            "Select bodies to modify properties",
            "Use scenario dropdown to change scenes",
            "",
            "Final Year Project 2025"
        ]
        
        y_offset = 10
        font = pygame.font.Font(None, 20)
        
        for line in help_text:
            if line.startswith("COSMIC"):
                color = (255, 255, 100)
                font_size = pygame.font.Font(None, 24)
            elif line.endswith(":"):
                color = (150, 200, 255)
                font_size = font
            else:
                color = (200, 200, 200)
                font_size = font
                
            text_surface = font_size.render(line, True, color)
            help_surface.blit(text_surface, (10, y_offset))
            y_offset += 16
            
        # Center help on screen
        help_rect = help_surface.get_rect()
        help_rect.center = (self.renderer.width // 2, self.renderer.height // 2)
        
        # Draw border
        pygame.draw.rect(self.renderer.screen, (100, 100, 120), help_rect, 2)
        self.renderer.screen.blit(help_surface, help_rect)
        
    def run(self) -> None:
        """Main application loop"""
        print("Starting Cosmic Collision Lab...")
        print("Controls: SPACE=pause, R=reset, T=trails, H=help")
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                
        except Exception as e:
            print(f"Application error: {e}")
            traceback.print_exc()
            
        finally:
            self.cleanup()
            
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.api_enabled and self.api_server:
            self.api_server.stop_server()
        self.renderer.cleanup()
        pygame.quit()


def main():
    """Main entry point"""
    try:
        app = CosmicCollisionLab()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()