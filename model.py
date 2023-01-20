import random
import uuid
from mesa import Model
from mesa.time import RandomActivation
from space import World
from shapely.geometry import Point
from agent import Critter, Species, critter_init_values, get_happiness_function
import math

class KinMaking(Model):
    height: int
    width: int
    pollution_rate: float
    sealing_rate: float
    sealevel_rise_rate: float
    human_expansion_rate: float
    mod_pollution: float
    sea_level: float
    init_sea_level: float
    init_global_temperature: float
    global_temperature: float
    temp_rise_rate: float
    temp_rise_exp: float
    crs: str
    num_critters: int
    population_reporters: dict
    population_charts: dict

    def __init__(
        self,
        height=512,
        width=512,
        pollution_rate=1.02,
        sealing_rate=1.05,
        sealevel_rise_rate=10,
        human_expansion_rate=1.05,
        temp_rise_rate=0.1,
        temp_rise_exp=1.02,
        init_mod_pollution=0,
        init_sea_level=0,
        init_global_temperature=21.0,
        init_num_critters=1,
        data_path=None,
        height_map_url="./data/jakarta_heightmap_2.png",
        seg_map_url="./data/jakarta_fake_2.png",
        min_h=-50,
        max_h=600
    ) -> None:
        super().__init__()
        self.crs = "epsg:3857"
        self.height = height
        self.width = width
        self.pollution_rate = pollution_rate
        self.sealing_rate = sealing_rate
        self.sealevel_rise_rate = sealevel_rise_rate
        self.human_expansion_rate = human_expansion_rate
        self.mod_pollution = init_mod_pollution
        self.init_sea_level = init_sea_level
        self.sea_level = init_sea_level
        self.init_global_temperature = init_global_temperature
        self.global_temperature = init_global_temperature
        self.temp_rise_rate = temp_rise_rate
        self.temp_rise_exp = temp_rise_exp
        self.init_num_critters = init_num_critters
        self.height_map_url = height_map_url
        self.seg_map_url = seg_map_url
        (self.min_h, self.max_h)=(min_h, max_h)
        
        self.schedule = RandomActivation(self)
        self._init_world(data_path)
        self._init_populations()
        self._init_critters(init_num_critters)
        self.initialize_data_collector(
                model_reporters={
                    "Overall Air Pollution": "pct_air_polluted",
                    "Overall Ground Pollution": "pct_ground_polluted",
                    "Percent Flooded": "pct_flooded",
                    "Percent Sealed Ground": "pct_sealed",
                    "Average Temperature": "avg_temp",
                    "Happy Critters": "happy_critters",
                    "Unhappy Critters": "unhappy_critters",
                    "Dead Critters": "dead_critters",
                    "Alive Critters": "alive_critters",
                    "New Critters": "new_critters",
                    **self.population_reporters
                }
        )

    @property
    def happy_critters(self) -> int:
        return len([critter for critter in self.space.agents if critter.is_happy and critter.is_alive])

    @property
    def unhappy_critters(self) -> int:
        return len([critter for critter in self.space.agents if not critter.is_happy and critter.is_alive])

    @property
    def dead_critters(self) -> int:
        return len([critter for critter in self.space.agents if not critter.is_alive])

    @property
    def alive_critters(self) -> int:
        return len([critter for critter in self.space.agents if critter.is_alive])

    @property
    def new_critters(self) -> int:
        return len([critter for critter in self.space.agents if critter.is_offspring])

    @property
    def pct_ground_polluted(self) -> float:
        total_poll = sum([cell.ground_pollution for cell in self.space.raster_layer])
        return 100 * total_poll / (self.width * self.height)

    @property
    def pct_air_polluted(self) -> float:
        total_poll = sum([cell.air_pollution for cell in self.space.raster_layer])
        return 100 * total_poll / (self.width * self.height)

    @property
    def pct_flooded(self) -> float:
        total_flooded = sum([cell.flooded for cell in self.space.raster_layer])
        return 100 * total_flooded / (self.width * self.height)

    @property
    def pct_sealed(self) -> float:
        total_sealed = sum([cell.sealing for cell in self.space.raster_layer])
        return 100 * total_sealed / (self.width * self.height)

    @property
    def avg_temp(self) -> float:
        total_d_temp = sum([cell.d_temp for cell in self.space.raster_layer])
        avg_d_temp = total_d_temp / (self.width * self.height)
        return self.global_temperature + avg_d_temp

    def step(self):
        self.global_temperature += self.temp_rise_rate * (self.temp_rise_rate**self.schedule.time) + 2*math.sin(0.25*math.pi*self.schedule.time)
        self.sea_level += self.sealevel_rise_rate
        self.schedule.step()
        self.datacollector.collect(self)

    def spawnCritter(self, species: Critter):
            if not len(critter_init_values[species]["biom_cells"]):
                return
            cell = random.choice(critter_init_values[species]["biom_cells"])
            (x,y) = (cell[1] - (self.width / 2), cell[2] - (self.height / 2))
            geometry = Point(x,y)
            critter = Critter(
                unique_id=uuid.uuid4().int,
                model=self,
                crs=self.crs,
                geometry=geometry,
                species=species,
                happinessFunction=get_happiness_function(species)
            )
            setattr(self, critter.species.value, getattr(self, critter.species.value) + 1)
            setattr(self, "init_{}".format(critter.species.value), getattr(self, critter.species.value) + 1)
            self.space.add_agents(critter)
            self.schedule.add(critter)

    def killCritter(self, critter: Critter):
        setattr(self, critter.species.value, getattr(self, critter.species.value) - 1)
        self.schedule.remove(critter)

    def _init_world(self, data_path):
        self.space = World(
            width=self.height,
            height=self.width,
            crs=self.crs,
            total_bounds=[-self.width / 2, -self.height / 2, self.width / 2, self.height / 2]
        )

        if data_path is not None:
            self.space.load_map(path=data_path, model=self)
        else:
            self.space.generate_map(model=self)
        for cell in self.space.raster_layer:
            self.schedule.add(cell)

    def _init_critters(self, num_critters: int):
        n = num_critters
        for species in list(Species):
            critter_init_values[species]["biom_cells"] = list(filter(
                lambda cell: cell[0].type in critter_init_values[species]["bioms"],
                self.space.raster_layer.coord_iter()
            ))
        for _ in range(num_critters):
            species = random.choice(list(Species))
            self.spawnCritter(species)

    def _init_populations(self):
        population_reporters = {}
        population_charts = []
        for species in list(Species):
            setattr(self, species.value, 0)
            setattr(self, "init_{}".format(species.value), 0)
            population_reporters["{} population".format(species.value)] = species.value
            population_charts.append(
                {"Label": "{} population".format(species.value), "Color": "Green"}
            )
        self.population_charts = population_charts
        self.population_reporters = population_reporters
