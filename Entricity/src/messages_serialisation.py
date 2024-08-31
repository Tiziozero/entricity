import json, struct
from typing import Dict
from sprites import Entity
class Serialiser:
    def __init__(self) -> None:
        self.sinfo: Dict[str, Dict[str, str]] = {}
        try:
            with open("message_serialisation_info.json", 'r') as f:
                self.sinfo = json.load(f)
        except FileNotFoundError:
            print("The file 'message_serialisation_info.json' was not found.")

        except json.JSONDecodeError:
            print("Error decoding the JSON file.")

    def get_serialization_info(self, key: str) -> Dict[str, str]:
        return self.sinfo.get(key, {})
    def serialize_entity(self, entity: Entity) -> bytes:
        entity_info = self.get_serialization_info("entity")

        serialized_data = bytearray()
        for field, dtype in entity_info.items():
            value = getattr(entity, field)
            if dtype == "uint16":
                serialized_data.extend(struct.pack('>H', value))
            elif dtype == "int":
                serialized_data.extend(struct.pack('>i', value))
            elif dtype == "uint8":
                serialized_data.extend(struct.pack('>B', value))
            else:
                raise ValueError(f"Unsupported data type: {dtype}")
        return bytes(serialized_data)
    def deserialize_entity(self, data: bytes) -> Entity:
        entity_info = self.get_serialization_info("entity")
        offset = 0
        kwargs = {}
        for field, dtype in entity_info.items():
            if dtype == "uint16":
                kwargs[field] = struct.unpack_from('>H', data, offset)[0]
                offset += 2
            elif dtype == "int":
                kwargs[field] = struct.unpack_from('>i', data, offset)[0]
                offset += 4
            elif dtype == "uint8":
                kwargs[field] = struct.unpack_from('>B', data, offset)[0]
                offset += 1
            else:
                raise ValueError(f"Unsupported data type: {dtype}")
        return Entity(**kwargs)


# Do some serius stuff here instead bruh
if __name__ == "__main__":
    s = Serialiser()

    e = Entity()
