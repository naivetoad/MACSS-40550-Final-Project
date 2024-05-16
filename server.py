import mesa
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from model import Gentrification
from agents import Resident, Immigrant, UrbanSlum

def agent_portrayal(agent):
    portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1}
    if isinstance(agent, Resident):
        portrayal["Color"] = "blue" if agent.moved_this_step else "green"
        portrayal["Layer"] = 1
        portrayal["text"] = round(agent.income, 1)
        portrayal["text_color"] = "white"
    elif isinstance(agent, Immigrant):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 1
        portrayal["text"] = round(agent.income, 1)
        portrayal["text_color"] = "white"
    elif isinstance(agent, UrbanSlum):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0  # Draw slums below agents if desired
    return portrayal

# Set up the canvas
grid = CanvasGrid(agent_portrayal, 60, 70, 600, 700)

average_income_chart = ChartModule(
    [{"Label": "Average Income", "Color": "Blue"}],
    data_collector_name='datacollector'
)

urban_slums_chart = ChartModule(
    [{"Label": "Urban Slums", "Color": "Black"}],
    data_collector_name='datacollector'
)

# Set up modifiable parameters
model_params = {
    "density": mesa.visualization.Slider("Agent Density", 0.35, 0.1, 1.0, 0.05),
    "width": 60,
    "height": 70,
    "immigrant_start": mesa.visualization.Slider("Immigrant Start", 100, 50, 300, 1),
    "immigrant_count": mesa.visualization.Slider("Immigrant Count", 50, 10, 200, 1),
    "income_variance": mesa.visualization.Slider("Income Variance", 0.25, 0.1, 1.0, 0.05),
    "preference": mesa.visualization.Slider("Preference", 0.5, 0.0, 1.0, 0.05)
}

# Set up the server
server = ModularServer(
    Gentrification,
    [grid, average_income_chart, urban_slums_chart],
    "Gentrification Model",
    model_params
)