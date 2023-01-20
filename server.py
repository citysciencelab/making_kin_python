from random import random
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter, Slider
from model import Species
from mesa_geo.visualization.modules import MapModule
from space import BiomCell, biom_init_values
from model import KinMaking, Critter, critter_init_values
import numpy as np

class GlobalTempText(TextElement):
    def __init__(self):
        pass
    
    def render(self, model: KinMaking):
        return "Avg. Air Temp.: {}, Total Temp. Rise: {}".format(
            round(model.avg_temp, 2),
            round(model.avg_temp - model.init_global_temperature, 2)
        )

class GlobalPopulationText(TextElement):
    def __init__(self):
        pass
    
    def render(self, model: KinMaking):
        return "Alive Critters: {}, Happy Critters: {}, Unhappy Critters: {}, Dead Critters {}, New Critters: {}".format(
            model.alive_critters,
            model.happy_critters,
            model.unhappy_critters,
            model.dead_critters,
            model.new_critters
        )

def clamp_rgb(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    (r,g,b) = [x if (0 <= x <= 255) else (0 if x < 0 else 255) for x in rgb]
    return (r,g,b)

def apply_heat_modifier(color: tuple[int, int, int], temp: float, deadly_temp: float = 42) -> tuple[int, int, int]:
    pct_deadly = temp / deadly_temp
    mod = (pct_deadly, 1-pct_deadly, 1-pct_deadly)
    rgb = (round(color[0]*mod[0]), round(color[1]*mod[1]), round(color[2]*mod[2]))
    return clamp_rgb(rgb=rgb)

def cell_portrayal(cell: BiomCell) -> tuple[float, float, float, float]:
    rgb = biom_init_values[cell.type]["color"]
    # rgb = (255,255,255)
    # rgb = apply_heat_modifier(color=rgb, temp=(cell.model.global_temperature + cell.d_temp))
    # alpha = cell.alt_norm
    # rgb = (255*cell.alt_norm, 255*cell.alt_norm, 255*cell.alt_norm)
    alpha = 1
    return (*rgb, alpha)

def critter_portrayal(critter: Critter) -> dict:
    if critter.is_alive:
        return {
            "radius": 2,
            "shape": "circle",
            "color": critter_init_values[critter.species]["color"],
            "fill": True,
            "fillOpacity": 1
        }
    else:
        return {
            "radius": 1, "color": [150,150,150,0.8]
        }

def draw(agent: BiomCell | Critter):
    if isinstance(agent, BiomCell):
        return cell_portrayal(agent)
    if isinstance(agent, Critter):
        return critter_portrayal(agent)
    return None

grid_size = (512, 512)
model_params = {
    "height": grid_size[0],
    "width": grid_size[1],
    "pollution_rate": Slider("Pollution Rate", 1.02, 0.5, 1.5, 0.01),
    "sealing_rate": Slider("Sealing Rate", 1.05, 0.5, 1.5, 0.01),
    "sealevel_rise_rate": Slider("Sealevel Rising Rate", 10, 0, 50, 1),
    "init_sea_level": Slider("Initial Sealevel", 0, -50, 150, 1),
    "min_h": Slider("Minimum Terrain height", -50, -200, 1000, 1),
    "max_h": Slider("Maximum Terrain height", 600, -200, 1000, 1),
    "human_expansion_rate": Slider("Human Expansion Rate", 1.05, 0.5, 1.5, 0.01),
    "temp_rise_rate": Slider("Global Temp Rise Rate", 0.1, 0.0, 1.0, 0.05),
    "temp_rise_exp": Slider("Global Temp Rise Exponent", 1.02, 1, 1.2, 0.01),
    "init_num_critters": Slider("Number of critters", 100, 1, 1000, 1)
}
map_module = MapModule(
    portrayal_method=draw,
    map_height=grid_size[1],
    map_width=grid_size[0],
    view=[0, 0],
    zoom=17.2,
)

temp_text = GlobalTempText()
pop_text = GlobalPopulationText()
chart_poll = ChartModule([
    {"Label": "Overall Air Pollution", "Color": "Red"},
    {"Label": "Overall Ground Pollution", "Color": "Green"},
    {"Label": "Percent Flooded", "Color": "Blue"},
    {"Label": "Percent Sealed Ground", "Color": "Brown"}
])

chart_temp = ChartModule([
    {"Label": "Average Temperature", "Color": "Pink"},
])

chart_population = ChartModule(
    [{"Label": "{} population".format(species.value), "Color": critter_init_values[species]["color"]} for species in list(Species)]
)

server = ModularServer(
    KinMaking,
    [map_module, temp_text, pop_text, chart_poll, chart_temp, chart_population],
    "Making Kin with Python",
    model_params,
)
