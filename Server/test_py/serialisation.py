from typing import List, Tuple
from sprites import Entity
import struct, pygame
from random import randint

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

"""
# send a byte that corresponds to an index and then data like:
0x00 for in server id uint16
0x01 for x which is a int32 i think idk
0x02 for y which is a int32 i think idk
0x03 for state which is a uint8
0x04 for dirrection which is a uint8
...eventually add extra fields here
"""

# doesn't add in server id
def serialise(e: Entity) -> bytes:
    data = bytearray()

    # print(f"{e.last_state['x']}:{e.pos.x}")
    if e.last_state.get('x') != e.pos.x:
        # print("Added x")
        data.append(0x01)
        data.extend(pack_int32(int(e.pos.x)))
        e.last_state['x'] = int(e.pos.x)

    # print(f"{e.last_state['y']}:{e.pos.y}")
    if e.last_state.get('y') != e.pos.y:
        # print("Added y")
        data.append(0x02)
        data.extend(pack_int32(int(e.pos.y)))
        e.last_state['y'] = int(e.pos.y)

    # print(f"{e.last_state['state']}:{e.state}")
    if e.last_state.get('state') != e.state:
        # print("Added state")
        data.append(0x03)
        data.extend(pack_uint8(e.state))
        e.last_state['state'] = int(e.state)

    # print(f"{e.last_state['direction']}:{e.direction}")
    if e.last_state.get('direction') != e.direction:
        # print("Added direction")
        data.append(0x04)
        data.extend(pack_uint8(e.direction))
        e.last_state['direction'] = int(e.direction)

    return bytes(data)

def serialise_entities(es: List[Entity]) -> bytes:
    data = bytearray()
    l = len(es)
    num_entities = struct.pack('B', l)
    data.extend(num_entities)

    for e in es:
        server_id = struct.pack('!H', e.in_server_id)
        data.append(0x00)
        data.extend(server_id)
        if e.last_state.get('x') != e.pos.x:
            data.append(0x01)
            data.extend(pack_int32(int(e.pos.x)))
            e.last_state['x'] = int(e.pos.x)

        if e.last_state.get('y') != e.pos.y:
            data.append(0x02)
            data.extend(pack_int32(int(e.pos.y)))
            e.last_state['y'] = int(e.pos.y)

        if e.last_state.get('state') != e.state:
            data.append(0x03)
            data.extend(pack_uint8(e.state))
            e.last_state['state'] = int(e.state)

        if e.last_state.get('direction') != e.direction:
            data.append(0x04)
            data.extend(pack_uint8(e.direction))
            e.last_state['direction'] = int(e.direction)

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

def deserialise(data: bytes) -> Entity:
    # only one entity including in server id
    i = 0
    # print(data)
    if data[i] != 0x00:
        raise Exception("Invalid data")
    i += 1
    in_server_id, i = unpack_uint16(data, i)
    entity = Entity()
    entity.in_server_id = in_server_id  
    while i < len(data):
        field_code = data[i]
        i += 1 # to move to data for unpack_... to have data iteslf without field code
        # print(field_code)
        if field_code == 0x01:
            # print(f"	x: {data[i:i+4]}")
            entity.pos.x, i = unpack_int32(data, i)
        elif field_code == 0x02:
            # print(f"	y: {data[i:i+4]}")
            entity.pos.y, i = unpack_int32(data, i)
        elif field_code == 0x03:
            # print(f"	state: {data[i:i+1]}")
            entity.state, i = unpack_uint8(data, i)
        elif field_code == 0x04:
            # print(f"dirrection: {data[i:i+1]}")
            entity.direction, i = unpack_uint8(data, i)
        # for multiple entities implementation
        elif field_code == 0x00:
            break
        else:
            raise Exception("Trailing invalid data")
    return entity


def deserialise_entities(data: bytes) -> List[Entity]:
    entities = []
    i = 0

    # !!! Can't use deserialise(data) because i should increment and it would
    #     be redundent to add i to deserialise

    # Get the number of entities
    num_entities, i = unpack_uint8(data, i)
    # sould be one. point at field code 0x00 server id
    # print("Deserialising entities: ",num_entities)

    while i < len(data):
        # Read the field code for server ID
        field_code = data[i]
        i += 1 # should point at field code
        # print(f"Field code: {field_code}")


        if field_code == 0x00:
            server_id, i = unpack_uint16(data, i)

            entity = Entity()
            entity.in_server_id = server_id
            entity.pos = pygame.Vector2(0,0)
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
                    entity.pos.x, i = unpack_int32(data, i)
                elif field_code == 0x02:
                    # print(f"\ty: {data[i:i+4]}")
                    entity.pos.y, i = unpack_int32(data, i)
                elif field_code == 0x03:
                    # print(f"\tstate: {data[i:i+1]}")
                    entity.state, i = unpack_uint8(data, i)
                elif field_code == 0x04:
                    # print(f"\tdirrection: {data[i:i+1]}")
                    entity.direction, i = unpack_uint8(data, i)
            entities.append(entity)

    return entities


if __name__ == "__main__":
    # test multiple entities
    def print_entities(es: List[Entity], msg:str=""):
        indent=""
        if msg != "":
            print(msg)
            indent = "\t"
        for e in es:
            print(f"{indent}Entity: {e.in_server_id}@{e.pos.x: >5}:{e.pos.y: >5}(s:{e.state};d:{e.direction}")
    entities = [
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
    ]
    print_entities(entities, "Before serialisation")
    serialised_entities = serialise_entities(entities)
    print("serialised_entities")
    deserialised_entities = deserialise_entities(serialised_entities)
    print_entities(deserialised_entities, "Deserialised entities:")
    
    # Test individual entities
    serialised_entities_array = []
    entities = [
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
        Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3)),
    ]
    print_entities(entities, "before serialising individual entities")
    for e in entities:
        b = bytearray()
        b.append(0x00)
        b.extend(pack_uint16(e.in_server_id))
        b.extend(serialise(e))
        serialised_entities_array.append(b)

    print("Serialised individual entities")
    deserialised_entities_array = []
    for e in serialised_entities_array:
        deserialised_entities_array.append(deserialise(e))
    print_entities(deserialised_entities_array, "Deserialised individual entities")
    """
    e = Entity(isid=randint(0, 1234),x=randint(-10000,10000),y=randint(-10000,10000),state=randint(0,3),direction=randint(0,3))
    print(f"Entity: {e.in_server_id}@{e.pos.x: >5}:{e.pos.y: >5}(s:{e.state};d:{e.direction}")
    serialised_e = bytearray()
    serialised_e.append(0x00)
    serialised_e.extend(pack_uint16(e.in_server_id))
    serialised_e.extend(serialise(e))
    deserialised_e = deserialise(serialised_e)
    print_entities([deserialised_e,],"Deserailised e:")
    """
    
