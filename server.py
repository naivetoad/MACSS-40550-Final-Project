import mesa
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from model import Gentrification
from agents import Resident, Immigrant, UrbanSlum, House

def agent_portrayal(agent):
    if agent is None:
        return
    
    portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1}
    
    if isinstance(agent, Resident) and not isinstance(agent, Immigrant):
        if agent.moved_this_step:
            portrayal["Color"] = "cyan"  # Color for agents that moved this step
        else:
            portrayal["Color"] = "green"
        portrayal["Layer"] = 1
    elif isinstance(agent, Immigrant):
        if agent.moved_this_step:
            portrayal["Color"] = "magenta"  # Color for immigrants that moved this step
        else:
            portrayal["Color"] = "red"
        portrayal["Layer"] = 1
    elif isinstance(agent, UrbanSlum):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0  # Draw slums below agents if desired
    elif isinstance(agent, House):
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 0
    
    return portrayal

# Set up the canvas
grid = CanvasGrid(
    portrayal_method=agent_portrayal,
    grid_width=20,
    grid_height=20,
    canvas_width=400,
    canvas_height=400,
)

# average_income_chart = ChartModule(
#     [{"Label": "Average Income", "Color": "Blue"}],
#     data_collector_name='datacollector'
# )

# urban_slums_chart = ChartModule(
#     [{"Label": "Urban Slums", "Color": "Black"}],
#     data_collector_name='datacollector'
# )

unhappy_agents_chart = ChartModule(
    [{"Label": "Unhappy Agents", "Color": "Red"}],
    data_collector_name='datacollector'
)

# average_utility_chart = ChartModule(
#     [{"Label": "Average Utility", "Color": "Green"}],
#     data_collector_name='datacollector'
# )

# Set up modifiable parameters 
model_params = {
    "density": mesa.visualization.Slider("Agent Density", 0.6, 0.1, 1.0, 0.05),
    "width": 20,
    "height": 20,
    "immigrant_start": mesa.visualization.Slider("Migrant Start", 20, 1, 300, 1),
    "immigrant_count": mesa.visualization.Slider("Migrant Count", 150, 1, 200, 1),
    "income_variance": mesa.visualization.Slider("Income Variance", 0.25, 0.1, 1.0, 0.05),
    "preference": mesa.visualization.Slider("Preference", 0.5, 0.0, 1.0, 0.05)
}

# Set up the server
server = ModularServer(
    Gentrification,
    [grid, unhappy_agents_chart],
    "Gentrification Model",
    model_params
)
