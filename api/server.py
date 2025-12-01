"""
FastAPI server for real-time simulation data access
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uvicorn
import threading
import time
import numpy as np
from physics.body import CelestialBody
from physics.physics_engine import PhysicsEngine
from simulation.scenarios import ScenarioManager
from config import API_HOST, API_PORT


# Pydantic models for API
class BodyCreate(BaseModel):
    """Model for creating a new celestial body"""
    name: str = Field(..., description="Name of the body")
    mass: float = Field(..., gt=0, description="Mass in kg")
    position: List[float] = Field(..., min_items=2, max_items=2, description="Position [x, y]")
    velocity: List[float] = Field(..., min_items=2, max_items=2, description="Velocity [vx, vy]")
    radius: float = Field(..., gt=0, description="Radius for visualization")
    color: List[int] = Field([100, 150, 255], min_items=3, max_items=3, description="RGB color")


class BodyUpdate(BaseModel):
    """Model for updating a celestial body"""
    name: Optional[str] = None
    mass: Optional[float] = Field(None, gt=0)
    position: Optional[List[float]] = Field(None, min_items=2, max_items=2)
    velocity: Optional[List[float]] = Field(None, min_items=2, max_items=2)
    radius: Optional[float] = Field(None, gt=0)
    color: Optional[List[int]] = Field(None, min_items=3, max_items=3)


class SimulationMetrics(BaseModel):
    """Model for simulation metrics"""
    time_elapsed: float
    body_count: int
    total_energy: float
    average_velocity: float
    center_of_mass: List[float]
    total_momentum: List[float]
    paused: bool


class APIServer:
    """FastAPI server for simulation control and data access"""
    
    def __init__(self, physics_engine: PhysicsEngine):
        self.physics_engine = physics_engine
        self.app = FastAPI(
            title="Cosmic Collision Lab API",
            description="REST API for controlling and accessing the astrophysics simulation",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Server state
        self.server_thread = None
        self.running = False
        
    def _setup_routes(self) -> None:
        """Setup all API routes"""
        
        @self.app.get("/", tags=["Info"])
        async def root():
            """Welcome message and API information"""
            return {
                "message": "Welcome to Cosmic Collision Lab API",
                "version": "1.0.0",
                "endpoints": {
                    "GET /objects": "Get all celestial bodies",
                    "GET /metrics": "Get simulation metrics",
                    "POST /add": "Add new celestial body",
                    "PUT /update/{body_id}": "Update celestial body",
                    "POST /pause": "Pause simulation",
                    "POST /resume": "Resume simulation",
                    "POST /reset": "Reset simulation",
                    "POST /scenario/{scenario_name}": "Load predefined scenario"
                }
            }
            
        @self.app.get("/objects", response_model=List[Dict[str, Any]], tags=["Simulation"])
        async def get_objects():
            """Get all celestial bodies in the simulation"""
            return [body.to_dict() for body in self.physics_engine.bodies if not body.merged]
            
        @self.app.get("/objects/{body_id}", response_model=Dict[str, Any], tags=["Simulation"])
        async def get_object(body_id: str):
            """Get a specific celestial body by ID"""
            try:
                body = self.physics_engine.get_body_by_id(body_id)
                if body.merged:
                    raise HTTPException(status_code=404, detail="Body has been merged")
                return body.to_dict()
            except ValueError:
                raise HTTPException(status_code=404, detail="Body not found")
                
        @self.app.get("/metrics", response_model=SimulationMetrics, tags=["Simulation"])
        async def get_metrics():
            """Get comprehensive simulation metrics"""
            stats = self.physics_engine.get_simulation_stats()
            return SimulationMetrics(**stats)
            
        @self.app.post("/add", response_model=Dict[str, str], tags=["Simulation"])
        async def add_object(body_data: BodyCreate):
            """Add a new celestial body to the simulation"""
            try:
                new_body = CelestialBody(
                    mass=body_data.mass,
                    position=np.array(body_data.position),
                    velocity=np.array(body_data.velocity),
                    radius=body_data.radius,
                    color=tuple(body_data.color),
                    name=body_data.name
                )
                
                self.physics_engine.add_body(new_body)
                return {"message": "Body added successfully", "id": new_body.id}
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to add body: {str(e)}")
                
        @self.app.put("/update/{body_id}", response_model=Dict[str, str], tags=["Simulation"])
        async def update_object(body_id: str, updates: BodyUpdate):
            """Update properties of a celestial body"""
            try:
                body = self.physics_engine.get_body_by_id(body_id)
                
                if body.merged:
                    raise HTTPException(status_code=404, detail="Body has been merged")
                
                # Apply updates
                update_data = updates.dict(exclude_unset=True)
                
                for field, value in update_data.items():
                    if field == "position":
                        body.position = np.array(value)
                    elif field == "velocity":
                        body.velocity = np.array(value)
                    elif field == "color":
                        body.color = tuple(value)
                    else:
                        setattr(body, field, value)
                        
                return {"message": "Body updated successfully"}
                
            except ValueError:
                raise HTTPException(status_code=404, detail="Body not found")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to update body: {str(e)}")
                
        @self.app.delete("/remove/{body_id}", response_model=Dict[str, str], tags=["Simulation"])
        async def remove_object(body_id: str):
            """Remove a celestial body from the simulation"""
            try:
                body = self.physics_engine.get_body_by_id(body_id)
                self.physics_engine.remove_body(body)
                return {"message": "Body removed successfully"}
                
            except ValueError:
                raise HTTPException(status_code=404, detail="Body not found")
                
        @self.app.post("/pause", response_model=Dict[str, str], tags=["Control"])
        async def pause_simulation():
            """Pause the simulation"""
            self.physics_engine.pause()
            return {"message": "Simulation paused"}
            
        @self.app.post("/resume", response_model=Dict[str, str], tags=["Control"])
        async def resume_simulation():
            """Resume the simulation"""
            self.physics_engine.resume()
            return {"message": "Simulation resumed"}
            
        @self.app.post("/reset", response_model=Dict[str, str], tags=["Control"])
        async def reset_simulation():
            """Reset the simulation (clear all bodies)"""
            self.physics_engine.clear_bodies()
            return {"message": "Simulation reset"}
            
        @self.app.get("/scenarios", response_model=List[str], tags=["Scenarios"])
        async def get_scenarios():
            """Get list of available predefined scenarios"""
            return list(ScenarioManager.get_all_scenarios().keys())
            
        @self.app.post("/scenario/{scenario_name}", response_model=Dict[str, str], tags=["Scenarios"])
        async def load_scenario(scenario_name: str):
            """Load a predefined cosmic scenario"""
            scenarios = ScenarioManager.get_all_scenarios()
            
            if scenario_name not in scenarios:
                available = list(scenarios.keys())
                raise HTTPException(
                    status_code=404, 
                    detail=f"Scenario '{scenario_name}' not found. Available: {available}"
                )
                
            try:
                # Clear existing bodies and load scenario
                self.physics_engine.clear_bodies()
                bodies = scenarios[scenario_name]()
                
                for body in bodies:
                    self.physics_engine.add_body(body)
                    
                return {"message": f"Scenario '{scenario_name}' loaded successfully"}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load scenario: {str(e)}")
                
        @self.app.get("/status", tags=["Info"])
        async def get_status():
            """Get server and simulation status"""
            return {
                "server_running": True,
                "simulation_paused": self.physics_engine.is_paused(),
                "body_count": len([b for b in self.physics_engine.bodies if not b.merged]),
                "simulation_time": self.physics_engine.time_elapsed,
                "uptime": time.time()
            }
            
    def start_server(self, host: str = API_HOST, port: int = API_PORT) -> None:
        """Start the API server in a background thread"""
        if self.running:
            print("Server is already running")
            return
            
        def run_server():
            self.running = True
            try:
                uvicorn.run(self.app, host=host, port=port, log_level="info")
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                self.running = False
                
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print(f"API server starting at http://{host}:{port}")
        
    def stop_server(self) -> None:
        """Stop the API server"""
        self.running = False
        if self.server_thread and self.server_thread.is_alive():
            # Note: uvicorn doesn't have a clean shutdown method when run this way
            # In production, you'd want to use uvicorn.Server with proper shutdown handling
            print("Server stopping...")
            
    def is_running(self) -> bool:
        """Check if the server is running"""
        return self.running


# Standalone server function for command-line usage
def create_standalone_server():
    """Create a standalone API server for testing"""
    from physics.physics_engine import PhysicsEngine
    
    # Create a physics engine with sample data
    engine = PhysicsEngine()
    
    # Load a default scenario
    solar_system = ScenarioManager.create_solar_system()
    for body in solar_system:
        engine.add_body(body)
        
    # Create and return server
    return APIServer(engine)


if __name__ == "__main__":
    # Run standalone server for testing
    server = create_standalone_server()
    
    print("Starting Cosmic Collision Lab API server...")
    print("Visit http://localhost:8000/docs for interactive API documentation")
    
    try:
        uvicorn.run(server.app, host=API_HOST, port=API_PORT, log_level="info")
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")