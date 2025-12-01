# 🌌 Cosmic Collision Lab

**Interactive 2D Astrophysics Simulator | Final Year Project 2025**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyGame](https://img.shields.io/badge/PyGame-2.6.1-green.svg)
![NumPy](https://img.shields.io/badge/NumPy-1.26.4-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![License](https://img.shields.io/badge/License-Educational-purple.svg)

An advanced physics simulation platform that brings astrophysics concepts to life through interactive visualization. Built with Python, PyGame, and NumPy, this application demonstrates real-time Newtonian gravity, collision physics, and orbital mechanics in an intuitive, educational environment.

## ✨ Features

### Core Physics
- **Real-time Newtonian gravity** - Accurate gravitational interactions between all bodies
- **Collision detection and merging** - Bodies merge realistically when they collide
- **Orbital mechanics** - Stable orbits, elliptical paths, and complex multi-body dynamics
- **Energy conservation** - Watch kinetic and potential energy change over time

### Interactive Visualization
- **Drag-and-drop interface** - Move celestial bodies with your mouse
- **Dynamic camera system** - Zoom and pan to follow the action
- **Orbit trails** - See the beautiful paths bodies take through space
- **Background star field** - Immersive space environment

### User Interface
- **Parameter sliders** - Adjust mass, radius, and velocity in real-time
- **Scenario selector** - Jump between predefined cosmic setups
- **Performance metrics** - FPS counter and simulation statistics
- **Keyboard shortcuts** - Quick access to all major functions

### Cosmic Scenarios
1. **Solar System** - Realistic planetary orbits around the Sun
2. **Galaxy Collision** - Two spiral galaxies merging over time
3. **Asteroid Impact** - High-velocity collision with debris effects  
4. **Binary System** - Twin stars with circumbinary planets
5. **Three-Body Problem** - Chaotic dynamics demonstration

### REST API
- **Real-time data access** - Monitor simulation state remotely
- **Remote control** - Pause, resume, and modify the simulation
- **Body management** - Add, remove, and update celestial bodies
- **Scenario loading** - Switch between scenarios programmatically

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project:**
```bash
git clone <repository-url>
cd Cosmic-Collision-Lab
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the simulator:**
```bash
python main.py
```

4. **Start the API server (optional):**
```bash
python api/server.py
```
or
```bash
uvicorn api.server:app --reload --host localhost --port 8000
```

## 🎮 Controls

### Mouse Controls
- **Left Click + Drag**: Select and move celestial bodies
- **Right Click + Drag**: Pan the camera view
- **Mouse Wheel**: Zoom in and out

### Keyboard Shortcuts
- **SPACE**: Pause/Resume simulation
- **R**: Reset simulation
- **T**: Toggle orbit trails
- **E**: Toggle educational information panel
- **I**: Toggle information panel
- **F**: Toggle FPS counter
- **U**: For opening and closing future work page
- **H** or **F1**: Show/hide help
- **W**: Dismiss welcome screen
- **ESC**: Deselect body or exit application

### UI Elements
- **Parameter Sliders**: Adjust properties of selected bodies
- **Control Buttons**: Access major functions
- **Scenario Dropdown**: Load predefined setups
- **Educational Panel**: Physics facts and real-time statistics
- **Toggle Switches**: Enable/disable features

## 📚 Educational Features

### Built-in Learning Content
The simulator includes comprehensive educational materials designed for learning and teaching:

#### Interactive Physics Demonstrations
- **Gravitational Force**: Visualize F = G × (m₁ × m₂) / r²
- **Orbital Mechanics**: Kepler's laws in action
- **Momentum Conservation**: Watch collisions preserve momentum
- **Energy Transfer**: Kinetic and potential energy interactions

#### Educational Information Panel (Press E)
Each scenario includes:
- **Scenario-Specific Facts**: Tailored educational content
- **Real-Time Statistics**: Live energy and momentum calculations
- **Physics Formulas**: Key equations displayed and explained
- **Astronomy Concepts**: Astrophysics principles in context

#### Scenario Learning Objectives

**Solar System**
- Understanding orbital periods and Kepler's laws
- Gravitational influence of massive bodies
- Stable vs. unstable orbital configurations

**Galaxy Collision**
- Galactic dynamics and dark matter effects
- Timescales of cosmic events
- Star formation in merging galaxies

**Asteroid Impact**
- Kinetic energy and impact physics
- Conservation of momentum in collisions
- Crater formation principles

**Binary System**
- Center of mass calculations
- Orbital resonance and stability
- Multiple star system dynamics

**Three-Body Problem**
- Chaotic systems and sensitivity to initial conditions
- Unpredictability in complex gravitational systems
- Numerical simulation limitations

### Academic Applications
- **Physics Courses**: Demonstrate Newtonian mechanics
- **Astronomy Classes**: Explore celestial dynamics
- **Programming Education**: Study numerical methods and simulation
- **Research Projects**: Test gravitational hypotheses

## 🌌 Scenarios Explained

### Solar System
A scientifically accurate representation of our solar system with:
- The Sun at the center with realistic mass
- Planets with correct relative sizes and orbital velocities
- Stable, long-term orbital dynamics

### Galaxy Collision
Witness the spectacular collision of two galaxies:
- Each galaxy contains a supermassive black hole at its center
- 25 stars per galaxy in realistic spiral patterns
- Different colored star populations (blue and red galaxies)
- Watch as gravitational forces reshape both galaxies

### Asteroid Impact
A dramatic high-velocity impact scenario:
- Earth-like planet surrounded by orbital debris
- Large asteroid approaching at high speed
- Realistic debris field that responds to gravity
- Observe the aftermath of the collision

### Binary System
A complex stellar system featuring:
- Two orbiting stars of different masses and colors
- Multiple planets in circumbinary orbits
- Demonstration of stable multi-body dynamics
- Beautiful figure-8 orbital patterns

### Three-Body Problem
A demonstration of chaotic dynamics:
- Three equal-mass bodies in unstable configuration
- Highly sensitive to initial conditions
- Unpredictable long-term behavior
- Classic physics problem visualization

## 🔧 API Documentation

The FastAPI server provides comprehensive control over the simulation:

### Base URL
```
http://localhost:8000
```

### Key Endpoints

#### Get All Bodies
```http
GET /objects
```
Returns detailed information about all celestial bodies.

#### Add New Body
```http
POST /add
Content-Type: application/json

{
  "name": "New Planet",
  "mass": 5.972e24,
  "position": [100, 0],
  "velocity": [0, 10],
  "radius": 15,
  "color": [100, 150, 255]
}
```

#### Control Simulation
```http
POST /pause        # Pause the simulation
POST /resume       # Resume the simulation  
POST /reset        # Clear all bodies
```

#### Load Scenarios
```http
POST /scenario/Solar%20System
POST /scenario/Galaxy%20Collision
POST /scenario/Asteroid%20Impact
```

#### Get Metrics
```http
GET /metrics
```
Returns comprehensive simulation statistics including energy, momentum, and body count.

### Interactive Documentation
Visit `http://localhost:8000/docs` for complete interactive API documentation with Swagger UI.

## 🏗️ Architecture

### Project Structure
```
cosmic_collision_lab/
├── main.py                 # Main application entry point
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
├── physics/              
│   ├── body.py            # CelestialBody class
│   └── physics_engine.py  # Core physics simulation
├── simulation/
│   ├── renderer.py        # PyGame visualization
│   └── scenarios.py       # Predefined cosmic scenarios
├── ui/
│   ├── sliders.py         # Parameter adjustment sliders
│   ├── buttons.py         # UI buttons and controls
│   └── drag_handler.py    # Mouse interaction handling
├── api/
│   └── server.py          # FastAPI REST server
└── assets/
    ├── fonts/             # Custom fonts (empty - uses system fonts)
    └── icons/             # UI icons (empty - uses simple shapes)
```

### Core Components

#### Physics Engine (`physics/`)
- **CelestialBody**: Individual objects with mass, position, velocity, and rendering properties
- **PhysicsEngine**: Manages gravitational forces, collisions, and time integration
- Uses Verlet integration for stable numerical simulation
- Implements realistic collision detection and inelastic merging

#### Rendering System (`simulation/`)
- **Renderer**: PyGame-based visualization with camera system
- **Camera**: Zoom, pan, and coordinate transformation
- **StarField**: Procedurally generated background stars
- Efficient rendering with view frustum culling

#### User Interface (`ui/`)
- **Sliders**: Real-time parameter adjustment with logarithmic scaling
- **Buttons**: Action triggers and toggle switches
- **DragHandler**: Mouse-based body manipulation with visual feedback
- Modular panel system for organized layout

#### API Server (`api/`)
- **FastAPI**: RESTful endpoints for simulation control
- **Pydantic**: Type-safe data models for requests/responses
- **CORS**: Cross-origin support for web integration
- **Threading**: Non-blocking server operation

## ⚙️ Configuration

Key settings in `config.py`:

### Physics Parameters
```python
GRAVITY_CONSTANT = 6.67430e-11  # Real gravitational constant
SCALE_FACTOR = 1e-9            # Spatial scaling factor  
TIME_SCALE = 86400             # Seconds per simulation frame
COLLISION_THRESHOLD = 0.8       # Collision detection sensitivity
```

### Display Settings  
```python
WINDOW_WIDTH = 1200            # Initial window width
WINDOW_HEIGHT = 800            # Initial window height
FPS = 60                       # Target frame rate
MAX_TRAIL_LENGTH = 100         # Maximum orbit trail points
```

### Visual Customization
```python
COLORS = {
    'sun': (255, 255, 100),
    'planet': (100, 150, 255),
    'moon': (200, 200, 200),
    'asteroid': (150, 100, 50)
}
```

## 🧪 Advanced Usage

### Creating Custom Scenarios
Add new scenarios to `simulation/scenarios.py`:

```python
@staticmethod
def create_custom_scenario() -> List[CelestialBody]:
    bodies = []
    
    # Create central star
    star = CelestialBody(
        mass=2e30,
        position=np.array([0, 0]),
        velocity=np.array([0, 0]),
        radius=25,
        color=(255, 200, 100),
        name="Central Star"
    )
    bodies.append(star)
    
    # Add orbiting planets
    for i in range(3):
        distance = 100 + i * 50
        orbital_velocity = np.sqrt(6.67430e-11 * star.mass / (distance * 1000)) * 0.001
        
        planet = CelestialBody(
            mass=1e24 * (i + 1),
            position=np.array([distance, 0]),
            velocity=np.array([0, orbital_velocity]),
            radius=10 + i * 3,
            color=(100 + i * 50, 150, 255 - i * 30),
            name=f"Planet {i + 1}"
        )
        bodies.append(planet)
    
    return bodies
```

### Extending the API
Add custom endpoints to `api/server.py`:

```python
@self.app.get("/custom-endpoint")
async def custom_function():
    # Your custom logic here
    return {"message": "Custom response"}
```

### Physics Modifications
Adjust physics behavior in `physics/physics_engine.py`:

```python
# Add custom forces
def apply_custom_force(self, body1, body2):
    # Implement magnetic forces, radiation pressure, etc.
    pass
```

## 🐛 Troubleshooting

### Common Issues

**Simulation runs too slow:**
- Reduce the number of bodies in the scenario
- Lower the FPS target in config.py
- Increase TIME_SCALE for faster simulation time

**Bodies fly apart immediately:**
- Check initial velocities are appropriate for orbital mechanics
- Verify mass values are realistic (use scientific notation)
- Adjust GRAVITY_CONSTANT scaling if needed

**UI elements not responding:**
- Ensure pygame events are being processed correctly
- Check that UI panels aren't overlapping
- Verify mouse coordinates are being transformed properly

**API server won't start:**
- Check that port 8000 isn't already in use
- Verify all dependencies are installed correctly
- Look for error messages in the console output

### Performance Optimization

For better performance with many bodies:
1. Implement spatial partitioning (quadtree/octree)
2. Use adaptive time stepping
3. Add level-of-detail for distant objects
4. Implement GPU acceleration with PyOpenGL

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- **New scenarios**: Add more interesting cosmic setups
- **Physics features**: Implement relativistic effects, tidal forces
- **UI enhancements**: Better visual design, more intuitive controls  
- **Performance**: Optimize for large numbers of bodies
- **Documentation**: Improve code comments and user guides

## 📄 License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## 🙏 Acknowledgments

- **Administrator**: For giving us a chance to work on this project
- **group members**: For giving their time and skills
- **NumPy**: Efficient numerical computations
- **PyGame**: Cross-platform game development
- **FastAPI**: Modern web API framework
- **Uvicorn**: ASGI server implementation
- **Pydantic**: Data validation and settings management

Built with ❤️ for space enthusiasts, physics students, and anyone curious about the cosmos!

---

*"The universe is not only stranger than we imagine, it is stranger than we can imagine." - J.B.S. Haldane*