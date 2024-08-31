from typing import List, Tuple
import struct

def pack_int32(value: int) -> bytes:
    return struct.pack('!i', value)

def pack_uint16(value: int) -> bytes:
    return struct.pack('!H', value)

def pack_uint8(value: int) -> bytes:
    return struct.pack('!B', value)

def unpack_int32(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = struct.unpack('!i', data[offset:offset+4])[0]
    return value, offset + 4

def unpack_uint16(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = struct.unpack('!H', data[offset:offset+2])[0]
    return value, offset + 2
def unpack_uint8(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = struct.unpack('!B', data[offset:offset+1])[0]
    return value, offset + 1

class Changed:
    def __init__(self, v, c) -> None:
        self.value = v
        self.changed = c

    def __repr__(self) -> str:
        return f"Change:{self.value}-{self.changed};"

class EntitySerialisationData:
    def __init__(self) -> None:
        self.in_server_id = 0
        self.posX: Changed = Changed(0, False)
        self.posY: Changed = Changed(0, False)
        self.state: Changed = Changed(0, False)
        self.direction: Changed = Changed(0, False)
        self.entityChanged: bool = False
    def setPosX(self, v):
        self.posX = Changed(v, True)
        self.entityChanged = True
    def setPosY(self, v):
        self.posY = Changed(v, True)
        self.entityChanged = True
    def setState(self, v):
        self.state = Changed(v, True)
        self.entityChanged = True
    def setDirection(self, v):
        self.direction = Changed(v, True)
        self.entityChanged = True
    def __repr__(self) -> str:
        return f"{self.in_server_id}(Changed:{self.entityChanged})@{self.posX}:{self.posY};(s:{self.state};d:{self.direction})"
        

"""
# send a byte that corresponds to an index and then data like:
0x00 for in server id uint16
0x01 for x which is a int32 i think idk
0x02 for y which is a int32 i think idk
0x03 for state which is a uint8
0x04 for dirrection which is a uint8
...eventually add extra fields here
"""

# don't implement EntitySerialisationData... not yet... I'm not ready
# doesn't add in server id
def serialise(e: EntitySerialisationData) -> bytes:
    data = bytearray()
    if e.posX.changed:
        data.append(0x01)
        data.extend(pack_int32(int(e.posX.value)))
    if e.posY.changed:
        data.append(0x02)
        data.extend(pack_int32(int(e.posY.value)))
    if e.state.changed:
        data.append(0x03)
        data.extend(pack_uint8(e.state.value))
    if e.direction.changed:
        data.append(0x04)
        data.extend(pack_uint8(e.direction.value))
    return bytes(data)

def serialise_entities(es: List[EntitySerialisationData]) -> bytes:
    data = bytearray()
    l = len(es)
    num_entities = struct.pack('B', l)
    data.extend(num_entities)

    for e in es:
        server_id = struct.pack('!H', e.in_server_id)
        entityData = serialise(e)
        if len(entityData) > 0:
            data.append(0x00)
            data.extend(server_id)
            data.extend(entityData)
    return bytes(data)

"""
# get number of entities as uint8
# then entities
eg:
    0x05                        # indicates 5 entities
    0x00 0x00 0x44              # indicates in server id of 68
    0x01 0x00 0x00 0x00 0xa5    # indicats position x (0x01) is 165 (0xa0)
    0x00 0x00 0x45              # indicates in server id of 69
    0x01 0x00 0x00 0x00 0x00    # indicats position x (0x01) is 0
    0x02 0x00 0x00 0x00 0x00    # indicats position y (0x02) is 0
    ...
"""

def deserialise(data: bytes) -> EntitySerialisationData:
    # only one entity including in server id
    i = 0
    # print(data)
    if data[i] != 0x00:
        raise Exception("Invalid data")
    i += 1
    in_server_id, i = unpack_uint16(data, i)
    entity = EntitySerialisationData()
    entity.in_server_id = in_server_id  
    while i < len(data):
        field_code = data[i]
        i += 1 # to move to data for unpack_... to have data iteslf without field code
        # print(field_code)
        if field_code == 0x01:
            # print(f"	x: {data[i:i+4]}")
            x, i = unpack_int32(data, i)
            entity.setPosX(x)
        elif field_code == 0x02:
            # print(f"	y: {data[i:i+4]}")
            y, i = unpack_int32(data, i)
            entity.setPosY(y)
        elif field_code == 0x03:
            # print(f"	state: {data[i:i+1]}")
            state, i = unpack_uint8(data, i)
            entity.setState(state)
        elif field_code == 0x04:
            # print(f"dirrection: {data[i:i+1]}")
            direction, i = unpack_uint8(data, i)
            entity.setDirection(direction)
        # for multiple entities implementation
        elif field_code == 0x00:
            break
        else:
            raise Exception("Trailing invalid data")
    return entity


def deserialise_entities(data: bytes) -> List[EntitySerialisationData]:
    entities = []
    i = 0

    # !!! Can't use deserialise(data) because i should increment and it would
    #     be redundent to add i to deserialise

    # Get the number of entities
    num_entities, i = unpack_uint8(data, i)
    # print(f"Deserialising {num_entities} entities...")
    # sould be one. point at field code 0x00 server id
    # print("Deserialising entities: ",num_entities)

    while i < len(data):
        # Read the field code for server ID
        field_code = data[i]
        i += 1 # should point at field code
        # print(f"Field code: {field_code}")


        if field_code == 0x00:
            server_id, i = unpack_uint16(data, i)

            entity = EntitySerialisationData()
            entity.in_server_id = server_id
            # print(f"For entity with isid: {server_id}:")

            while i < len(data):
                field_code = data[i]
                # print(f"Field code: {field_code}")
                i += 1 # point at data
                if field_code == 0x00:
                    # If a new entity starts, break the loop
                    i -= 1
                    break
                elif field_code == 0x01:
                    # print(f"\tx: {data[i:i+4]}")
                    x, i = unpack_int32(data, i)
                    entity.setPosX(x)
                elif field_code == 0x02:
                    # print(f"\ty: {data[i:i+4]}")
                    y, i = unpack_int32(data, i)
                    entity.setPosY(y)
                elif field_code == 0x03:
                    # print(f"\tstate: {data[i:i+1]}")
                    state, i = unpack_uint8(data, i)
                    entity.setState(state)
                elif field_code == 0x04:
                    # print(f"\tdirrection: {data[i:i+1]}")
                    direction, i = unpack_uint8(data, i)
                    entity.setDirection(direction)
            # print("In multiple:", entity)
            if entity.entityChanged:
                entities.append(entity)

    return entities


def testSerialisation():
    def create_entity(entity_id: int, x: int, y: int, state: int, direction: int) -> EntitySerialisationData:
        entity = EntitySerialisationData()
        entity.in_server_id = entity_id
        entity.setPosX(x)
        entity.setPosY(y)
        entity.setState(state)
        entity.setDirection(direction)
        return entity

    # Test Case 1: Normal Data
    entity1 = create_entity(1, 100, 200, 50, 75)
    entity2 = create_entity(2, -1000, 5000, 100, 200)

    entities = [entity1, entity2]
    serialized_data = serialise_entities(entities)
    deserialized_entities = deserialise_entities(serialized_data)

    assert len(entities) == len(deserialized_entities), "Mismatch in number of entities"

    for original, deserialized in zip(entities, deserialized_entities):
        assert original.in_server_id == deserialized.in_server_id, f"Server ID mismatch: {original.in_server_id} != {deserialized.in_server_id}"
        assert original.posX.value == deserialized.posX.value, f"Position X mismatch: {original.posX.value} != {deserialized.posX.value}"
        assert original.posY.value == deserialized.posY.value, f"Position Y mismatch: {original.posY.value} != {deserialized.posY.value}"
        assert original.state.value == deserialized.state.value, f"State mismatch: {original.state.value} != {deserialized.state.value}"
        assert original.direction.value == deserialized.direction.value, f"Direction mismatch: {original.direction.value} != {deserialized.direction.value}"

    # Test Case 2: Edge Case - Maximum and Minimum Values
    max_entity = create_entity(3, 2**31 - 1, -(2**31), 255, 255)
    min_entity = create_entity(4, -(2**31), 2**31 - 1, 0, 0)

    entities = [max_entity, min_entity]
    serialized_data = serialise_entities(entities)
    deserialized_entities = deserialise_entities(serialized_data)

    assert len(entities) == len(deserialized_entities), "Mismatch in number of entities (edge case)"

    for original, deserialized in zip(entities, deserialized_entities):
        assert original.in_server_id == deserialized.in_server_id, f"Server ID mismatch (edge case): {original.in_server_id} != {deserialized.in_server_id}"
        assert original.posX.value == deserialized.posX.value, f"Position X mismatch (edge case): {original.posX.value} != {deserialized.posX.value}"
        assert original.posY.value == deserialized.posY.value, f"Position Y mismatch (edge case): {original.posY.value} != {deserialized.posY.value}"
        assert original.state.value == deserialized.state.value, f"State mismatch (edge case): {original.state.value} != {deserialized.state.value}"
        assert original.direction.value == deserialized.direction.value, f"Direction mismatch (edge case): {original.direction.value} != {deserialized.direction.value}"

    # Test Case 3: No Changes
    unchanged_entity = EntitySerialisationData()
    unchanged_entity.in_server_id = 5
    serialized_data = serialise_entities([unchanged_entity])
    deserialized_entities = deserialise_entities(serialized_data)

    assert len(deserialized_entities) == 0, "Unexpected number of entities in no-change case"
    # in no change happens then no entity should be sent
    # assert deserialized_entities[0].in_server_id == unchanged_entity.in_server_id, "Server ID mismatch in no-change case"

    # Test Case 4: Invalid Data (should raise Exception)
    try:
        deserialise(b'\x01\x00\x00\x00')
    except Exception as e:
        print("Properly caught an exception for invalid data:", str(e))

    print("All tests passed successfully.")


# Run the test
if __name__ == "__main__":
    testSerialisation()

