from enum import Enum
import math
import random
import uuid
from mesa_geo import GeoAgent
from space import BiomType, BiomCell
from shapely.geometry import Point
import happinessFunctions

class Diet(Enum):
    CARNIVORE = 0
    HERBIVORE = 1
    OMNIVORE = 2

class Species(Enum):
    ROACH = "roach"
    BUTTERFLY = "butterfly"
    SONGBIRD = "songbird"
    RAPTOR = "raptor"
    RODENT = "rodent"
    MONKEY = "monkey"
    CANINE = "canine"
    CRAB = "crab"
    FISH = "bass"
    SEAL = "seal"

def get_norm_vector(vector: tuple[float, float], l = 1):
    dist = math.sqrt(vector[0]**2 + vector[1]**2)
    return ((vector[0] / dist) * l, (vector[1] / dist) * l)

def defaultHappinessFunc(self):
    species_values = critter_init_values[self.species]
    current_cell = self._get_current_cell()
    neighbors = list(self.model.space.get_neighbors_within_distance(agent=self, distance=self.sensing_radius)) if len(self.model.space.agents) > 1 else []
    same_species, predator_species, prey_species, other_species = [], [], [], []
    for critter in neighbors:
        if critter.species == self.species: same_species.append(critter)
        elif critter.species in species_values["predators"]: predator_species.append(critter)
        elif self.species in critter_init_values[critter.species]["predators"]: prey_species.append(critter)
        else: other_species.append(critter)
    if not current_cell.type in species_values["bioms"]: return False
    if len([*other_species, *prey_species]) == 0: return False
    if len(same_species) < 2: return False
    if len(same_species) > 5: return False
    if len(same_species) <= len(predator_species): return False
    if species_values["diet"] == Diet.CARNIVORE and len(prey_species) == 0: return False
    if current_cell.air_pollution > species_values["res_air_p"]: return False
    if current_cell.ground_pollution > species_values["res_ground_p"]: return False
    if current_cell.sealing > species_values["res_sealing"]: return False
    if self.model.global_temperature + current_cell.d_temp > species_values["max_temp"]: return False

    return True

def get_happiness_function(species: Species):
    return critter_init_values[species]["happinessFunction"] if critter_init_values[species]["happinessFunction"] != None else defaultHappinessFunc

critter_init_values = {
    Species.BUTTERFLY: {
        "bioms": [BiomType.FOREST, BiomType.PARK, BiomType.RIVER, BiomType.MEADOW],
        "predators": [Species.SONGBIRD],
        "diet": Diet.HERBIVORE,
        "res_air_p": 0.5,
        "res_ground_p": 0.5,
        "res_sealing": 0.5,
        "max_temp": 28.0,
        "reproduction_rate": 5,
        "color": "yellow",
        "happinessFunction": happinessFunctions.butterfly
    },
    Species.SONGBIRD: {
        "bioms": [BiomType.FOREST, BiomType.PARK, BiomType.RIVER, BiomType.URBAN, BiomType.MEADOW],
        "predators": [Species.RAPTOR],
        "diet": Diet.OMNIVORE,
        "res_air_p": 0.4,
        "res_ground_p": 0.4,
        "res_sealing": 0.5,
        "max_temp": 28.0,
        "reproduction_rate": 4,
        "color": "orange",
        "happinessFunction": None
    },
    Species.RAPTOR: {
        "bioms": [BiomType.FOREST, BiomType.PARK, BiomType.RIVER, BiomType.ROAD, BiomType.ROCK, BiomType.COASTAL, BiomType.HARBOUR, BiomType.BEACH, BiomType.MEADOW],
        "diet": Diet.CARNIVORE,
        "predators": [],
        "res_air_p": 0.4,
        "res_ground_p": 0.6,
        "res_sealing": 0.5,
        "max_temp": 28.0,
        "reproduction_rate": 5,
        "color": "brown",
        "happinessFunction": None
    },
    Species.RODENT: {
        "bioms": [BiomType.PARK, BiomType.RIVER, BiomType.URBAN, BiomType.INDUSTRIAL, BiomType.HARBOUR, BiomType.MEADOW],
        "predators": [Species.CANINE, Species.RAPTOR],
        "diet": Diet.OMNIVORE,
        "res_air_p": 0.7,
        "res_ground_p": 0.8,
        "res_sealing": 0.9,
        "max_temp": 28.0,
        "reproduction_rate": 3,
        "color": "blue",
        "happinessFunction": None
    },
    Species.MONKEY: {
        "bioms": [BiomType.PARK, BiomType.FOREST],
        "predators": [Species.CANINE],
        "diet": Diet.OMNIVORE,
        "res_air_p": 0.5,
        "res_ground_p": 0.4,
        "res_sealing": 0.3,
        "max_temp": 28.0,
        "reproduction_rate": 6,
        "color": "green",
        "happinessFunction": None
    },
    Species.CANINE: {
        "bioms": [BiomType.PARK, BiomType.FOREST, BiomType.INDUSTRIAL, BiomType.URBAN, BiomType.HARBOUR, BiomType.MEADOW],
        "predators": [],
        "diet": Diet.OMNIVORE,
        "res_air_p": 0.5,
        "res_ground_p": 0.5,
        "res_sealing": 0.5,
        "max_temp": 28.0,
        "reproduction_rate": 5,
        "color": "pink",
        "happinessFunction": None
    },
    Species.CRAB: {
        "bioms": [BiomType.COASTAL, BiomType.RIVER, BiomType.HARBOUR, BiomType.BEACH, BiomType.ROCK],
        "predators": [Species.RAPTOR, Species.FISH],
        "diet": Diet.HERBIVORE,
        "res_air_p": 0.5,
        "res_ground_p": 0.5,
        "res_sealing": 0.5,
        "max_temp": 28.0,
        "reproduction_rate": 3,
        "color": "purple",
        "happinessFunction": None
    },
    Species.FISH: {
        "bioms": [BiomType.COASTAL, BiomType.OCEAN, BiomType.RIVER],
        "predators": [Species.SEAL],
        "diet": Diet.OMNIVORE,
        "res_air_p": 0.9,
        "res_ground_p": 0.4,
        "res_sealing": 0,
        "max_temp": 23.0,
        "reproduction_rate": 4,
        "color": "gold",
        "happinessFunction": None
    },
    Species.SEAL: {
        "bioms": [BiomType.COASTAL, BiomType.OCEAN, BiomType.HARBOUR, BiomType.BEACH, BiomType.ROCK],
        "predators": [],
        "diet": Diet.CARNIVORE,
        "res_air_p": 0.5,
        "res_ground_p": 0.5,
        "res_sealing": 0.5,
        "max_temp": 28.0,
        "reproduction_rate": 6,
        "color": "red",
        "happinessFunction": None
    },
    Species.ROACH: {
        "bioms": [BiomType.HARBOUR, BiomType.INDUSTRIAL, BiomType.ROAD, BiomType.URBAN, BiomType.PARK, BiomType.MEADOW],
        "predators": [Species.RODENT, Species.SONGBIRD],
        "diet": Diet.OMNIVORE,
        "res_air_p": 0.8,
        "res_ground_p": 0.9,
        "res_sealing": 1,
        "max_temp": 32.0,
        "reproduction_rate": 2,
        "color": "black",
        "happinessFunction": None
    }
}

class Critter(GeoAgent):
    species: Species
    is_happy: bool
    is_alive: bool
    is_offspring: bool
    steps_unhappy: int
    steps_happy: int
    sensing_radius: int
    move_speed: int

    def __init__(self, unique_id, model, geometry, crs, species, happinessFunction=defaultHappinessFunc, is_offspring=False) -> None:
        super().__init__(unique_id, model, geometry, crs)
        self.species = species
        self.steps_unhappy = 0
        self.steps_happy = 0
        self.dx = 0
        self.dy = 0
        self.sensing_radius = 40
        self.move_speed = 10
        self.is_happy = True
        self.is_alive = True
        self.is_offspring = is_offspring
        self._happinessFunction = happinessFunction.__get__(self, Critter)

    def calculate_happiness(self):
        self.is_happy = self._happinessFunction()
        self.steps_unhappy = self.steps_unhappy + 1 if not self.is_happy else 0
        self.steps_happy = self.steps_happy + 1 if self.is_happy else 0

    def step(self):
        # print("it's me {}, a {}".format(self.unique_id, self.species))
        self.calculate_happiness()
        if self.is_happy:
            # print("I'm happy since {} steps".format(self.steps_happy))
            (self.dx, self.dy) = (0, 0)
            if self.steps_happy > critter_init_values[self.species]["reproduction_rate"]:
                self.reproduce()
            else:
                self.roam()
        else:
            # print("I'm unhappy since {} steps".format(self.steps_unhappy))
            if self.steps_unhappy > 5:
                self.die()
            else:
                self.migrate()

    def reproduce(self):
        # print("procreating <3")
        critter = Critter(
            unique_id=uuid.uuid4().int,
            model=self.model,
            crs=self.crs,
            geometry=self.geometry,
            species=self.species,
            happinessFunction=get_happiness_function(self.species),
            is_offspring=True
        )
        self.model.space.add_agents(critter)
        self.model.schedule.add(critter)
        setattr(
            self.model,
            critter.species.value,
            getattr(self.model, critter.species.value) + 1
        )

    def die(self):
        # print("it's too late for me...x.x")
        self.is_alive = False
        self.model.killCritter(self)

    def migrate(self):
        # print("trying to get somewhere better")
        if (self.dx, self.dy) == (0, 0):
            return self._get_route()
        newPos = Point(
            self.geometry.x + self.dx,
            self.geometry.y + self.dy
        )
        # check whether the critter would move off the map
        if self.model.space.is_out_of_map_bounds(newPos):
            (self.dx, self.dy) = (0,0)
            return self.migrate()
        self.geometry = newPos
    
    def roam(self):
        # print("roaming...")
        newPos = Point(
            self.geometry.x + random.random() * 2,
            self.geometry.y + random.random() * 2
        )
        # check whether the critter would move off the map
        if self.model.space.is_out_of_map_bounds(newPos):
            return self.roam()
        self.geometry = newPos

    def _get_route(self):
        suitable_neighbors = self._get_suitable_neighbors()
        if len(suitable_neighbors) > 0:
            # print("I have {} suitable neighbors".format(len(suitable_neighbors)))
            destination = random.choice(suitable_neighbors)
            vector = (destination.pos[0] - self.grid_pos[0], destination.pos[1] - self.grid_pos[1])
            (self.dx, self.dy) = get_norm_vector(vector, l=self.move_speed)
        else:
            # print("Taking on a new random route")
            d = random.random() * 2*math.pi
            (self.dx, self.dy) = (self.move_speed*math.sin(d), self.move_speed*math.cos(d))
        self.migrate()

    def _get_suitable_neighbors(self):
        neighbors = list(self.model.space.raster_layer.get_neighboring_cells(
            pos=self.grid_pos, radius=self.sensing_radius, moore=False)
        )
        return list(filter(
            lambda neighbor: isinstance(neighbor, BiomCell) and neighbor.type in critter_init_values[self.species]["bioms"], neighbors
        ))

    def _get_current_cell(self):
        return self.model.space.raster_layer[self.grid_pos]

    @property
    def grid_pos(self) -> tuple[int, int]:
        return self.model.space.get_cell_pos_of_geom(self.geometry)

    def _happinessFunction(self):
        pass