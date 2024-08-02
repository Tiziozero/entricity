import json
from random import randint, random

bounds = (1000,1000)

i = 0
def make_entity():
    entity = {}
    entity["x"] = randint(0, bounds[0])
    entity["y"] = randint(0, bounds[1])
    entity["state"] = 1
    entity["direction"] = 12
    return entity
def make_map_entities(entities:int=10):
    with open(f"map_{i}.json", "w") as f:
        data = []
        for _ in range(10):
            data.append(make_entity())
        f.write(json.dumps(data))

if __name__ == "__main__":
    make_map_entities(10)

