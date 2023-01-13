from enum import Enum
import math
import random
from mesa_geo import Cell, RasterLayer
from mesa_geo.geospace import GeoSpace
from mesa import Model
from shapely.geometry import Point
import numpy as np
from PIL import Image, ImageOps

def simple_terrain (pos: tuple[float, float]) -> float:
    x = 10*pos[0]
    y = pos[1]
    return 100*(math.atan(x-2)+(0.1*math.sin((2*x)+1))-(0.04*math.sin(((7*x)+1))) + 0.2*math.sqrt(y)+(0.02*math.sin(13*y)))

class BiomType(Enum):
    OCEAN = 0
    COASTAL = 1
    BEACH = 2
    HARBOUR = 3
    URBAN = 4
    PARK = 5
    INDUSTRIAL = 6
    ROAD = 7
    FOREST = 8
    RIVER = 9
    ROCK = 10
    MEADOW = 11

biom_init_values = {
    BiomType.OCEAN: {
        "air_pollution": 0.2,
        "ground_pollution": 0.4,
        "sealing": 0,
        "d_temp": -5,
        "color": (46,156,191)
    },
    BiomType.COASTAL: {
        "air_pollution": 0.3,
        "ground_pollution": 0.5,
        "sealing": 0,
        "d_temp": -3,
        "color": (90,149,255)
    },
    BiomType.BEACH: {
        "air_pollution": 0.3,
        "ground_pollution": 0.4,
        "sealing": 0,
        "d_temp": 0,
        "color": (255,229,135)
    },
    BiomType.HARBOUR: {
        "air_pollution": 0.4,
        "ground_pollution": 0.5,
        "sealing": 0,
        "d_temp": 1,
        "color": (180,180,180)
    },
    BiomType.URBAN: {
        "air_pollution": 0.5,
        "ground_pollution": 0.5,
        "sealing": 0.8,
        "d_temp": 3,
        "color": (200,200,200)
    },
    BiomType.PARK: {
        "air_pollution": 0.3,
        "ground_pollution": 0.3,
        "sealing": 0.2,
        "d_temp": -2,
        "color": (168,219,102)
    },
    BiomType.INDUSTRIAL: {
        "air_pollution": 0.6,
        "ground_pollution": 0.6,
        "sealing": 0.8,
        "d_temp": 5,
        "color": (179,145,106) 
    },
    BiomType.FOREST: {
        "air_pollution": 0.1,
        "ground_pollution": 0.2,
        "sealing": 0.1,
        "d_temp": -3,
        "color": (40,156,82)
    },
    BiomType.ROAD: {
        "air_pollution": 0.4,
        "ground_pollution": 0.3,
        "sealing": 1.0,
        "d_temp": 1,
        "color": (100,100,100) 
    },
    BiomType.RIVER: {
        "air_pollution": 0.3,
        "ground_pollution": 0.4,
        "sealing": 0,
        "d_temp": -1,
        "color": (76,167,179)
    },
    BiomType.MEADOW: {
        "air_pollution": 0.3,
        "ground_pollution": 0.3,
        "sealing": 0,
        "d_temp": 0,
        "color": (136,221,61)
    },
    BiomType.ROCK: {
        "air_pollution": 0.2,
        "ground_pollution": 0.2,
        "sealing": 1,
        "d_temp": 1,
        "color": (140,140,140)
    },
}

class BiomCell(Cell):
    type: BiomType | None
    flooded: bool | None
    air_pollution: float | None
    ground_pollution: float | None
    sealing: float | None
    d_temp: float | None
    altitude: float | None
    alt_norm: float | None
    model: Model | None
    height_map: np.ndarray | None
    seg_map: np.ndarray | None


    def __init__(
        self, 
        pos=None, 
        indices=None
    ):
        super().__init__(pos, indices)
        self.flooded = False
        self.altitude = 0
        self.alt_norm = 0

    def _get_flooded(self, init=False):
        if self.altitude <= self.model.sea_level:
            self.flooded = True
            if self.model.sea_level - self.altitude > 20:
                self.type = BiomType.OCEAN
            else:
                self.type = BiomType.COASTAL

    def step(self):
        mod = random.gauss(0, 0.1)
        self.air_pollution *= (self.model.pollution_rate + mod)
        self.ground_pollution *= (self.model.pollution_rate + mod)
        self.sealing *= (self.model.sealing_rate + mod)
        self.d_temp *= (self.model.temp_rise_exp + mod)
        self._clamp_data()
        self._get_flooded()

    def _clamp_data(self):
        if self.air_pollution >= 1: self.air_pollution = 1
        if self.ground_pollution >= 1: self.ground_pollution = 1
        if self.sealing >= 1: self.sealing = 1

    def init_values(self, init_values=biom_init_values):
        self._get_flooded(init=True)
        self.air_pollution = init_values[self.type]["air_pollution"]
        self.ground_pollution = init_values[self.type]["ground_pollution"]
        self.sealing = init_values[self.type]["sealing"]
        self.d_temp = init_values[self.type]["d_temp"]


    
class World(GeoSpace):
    @property
    def raster_layer(self):
        return self.layers[0]

    def __init__(
        self,
        width,
        height,
        crs,
        total_bounds
    ):
        super().__init__(crs)
        self.add_layer(
            RasterLayer(
                width,
                height,
                crs,
                total_bounds,
                cell_cls=BiomCell
            )
        )

    def load_map(self, path, model):
        return

    def generate_map(self, model):
        cell: BiomCell

        self._load_heightmap(url=model.height_map_url, min_h=model.min_h, max_h=model.max_h)
        self._load_seg_map(url=model.seg_map_url)
        for cell in self.raster_layer:
            cell.type = self._get_cell_biom_type(cell.pos)
            cell.model = model
            cell.init_values()
            cell.step()

    def _load_heightmap(
        self,
        min_h=-50,
        max_h=600,
        url="./data/jakarta_heightmap_2.png"
    ):
        img_rgba = Image.open(url)
        img_gs = np.array(ImageOps.grayscale(img_rgba)) / 255
        self.height_map = np.interp(img_gs, (0, 1), (min_h, max_h))
        self.raster_layer.apply_raster(np.array([img_gs]), attr_name="alt_norm")
        self.raster_layer.apply_raster(np.array([self.height_map]), attr_name="altitude")

    def _load_seg_map(
        self,
        url="./data/jakarta_fake_2.png"
    ):
        img_rgba = Image.open(url)
        img_rgb = img_rgba.convert("RGB")
        self.seg_map = np.array(img_rgb.rotate(270))


    def get_cell_pos_of_geom(self, pt: Point):
        return (
            int(pt.x + (self.raster_layer._width / 2)),
            int(pt.y + (self.raster_layer._height / 2))
        )

    def get_rel_cell_pos(self, pos):
        return (pos[0] / self.raster_layer._width, pos[1] / self.raster_layer._height)

    def is_out_of_map_bounds(self, pt: Point):
        is_out_of_bounds = False
        pos = self.get_cell_pos_of_geom(pt)
        try:
            cell = self.raster_layer[pos]
        except:
           is_out_of_bounds = True
        return is_out_of_bounds

    def _get_cell_biom_type(self, pos: tuple[float,float]) -> BiomType:
        rgb = self.seg_map[pos]
        for biom_type in BiomType:
            if biom_init_values[biom_type]["color"] == tuple(rgb):
                return biom_type
        return BiomType.ROCK
        # pct_x,pct_y = pos

        # # some random elements
        # if 0.34 < pct_y < 0.35 and pct_x >= 0.2:
        #     return BiomType.ROAD
        # if 0.2 < pct_y < 0.24 and pct_x >= 0.2:
        #     return BiomType.RIVER

        # if pct_x < 0.15:
        #     return BiomType.ROCK
        # if pct_x < 0.3:
        #     if pct_y < 0.3 or pct_y > 0.7:
        #         return BiomType.BEACH
        #     return BiomType.HARBOUR
        # if pct_x < 0.7:
        #     if pct_x > 0.4 and (0.35 < pct_y < 0.65):
        #         return BiomType.PARK
        #     return BiomType.URBAN
        # if pct_x < 0.8 and pct_y > 0.75:
        #         return BiomType.MEADOW
        # if pct_x < 0.9:
        #     if pct_y > 0.75:
        #         return BiomType.MEADOW
        #     return BiomType.INDUSTRIAL
        # else:
        #     return BiomType.FOREST

