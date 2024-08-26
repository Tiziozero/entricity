from typing import List, Tuple
import struct
from random import randint

ISID_YES        = 0b00000001
X_YES           = 0b00000010
Y_YES           = 0b00000100
STATE_YES       = 0b00001000
DIRECTION_YES   = 0b00010000


class retVal:
    def __init__(self):
        self.isid:int = -1
        self.x:int|None = None
        self.y:int|None = None
        self.state:int|None = None
        self.direction:int|None = None

    def __repr__(self):
        attributes = []
        if self.isid is not None:
            attributes.append(f"isid: {self.isid}")
        if self.x is not None:
            attributes.append(f"x: {self.x}")
        if self.y is not None:
            attributes.append(f"y: {self.y}")
        if self.state is not None:
            attributes.append(f"state: {self.state}")
        if self.direction is not None:
            attributes.append(f"direction: {self.direction}")
        return " | ".join(attributes)
    def __eq__(self, other):
        if not isinstance(other, retVal):
            return NotImplemented
        return (self.isid == other.isid and self.x == other.x and
                self.y == other.y and self.state == other.state and

                self.direction == other.direction)

def pack_int32(value: int) -> bytes:
    return struct.pack('!i', value)

def pack_uint16(value: int) -> bytes:
    return struct.pack('!H', value)

def pack_uint8(value: int) -> bytes:

    return struct.pack('!B', value)

def unpack_uint32(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = struct.unpack('!I', data[offset:offset+4])[0]
    return value, offset + 4
def unpack_int32(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = struct.unpack('!i', data[offset:offset+4])[0]
    return value, offset + 4

def unpack_uint16(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = struct.unpack('!H', data[offset:offset+2])[0]
    return value, offset + 2
def unpack_uint8(data: bytes, offset: int = 0) -> Tuple[int, int]:
    value = struct.unpack('!B', data[offset:offset+1])[0]
    return value, offset + 1

def serialise(isid:int, x=None, y=None, state=None, direction=None) -> bytes:
    data = bytearray()
    i = 0
    i |= ISID_YES
    data.extend(pack_uint16(isid))
    if x is not None:
        i |= X_YES
        data.extend(pack_int32(x))
    if y is not None:
        i |= Y_YES
        data.extend(pack_int32(y))
    if state is not None:
        i |= STATE_YES
        data.extend(pack_uint8(state))
    if direction is not None:
        i |= DIRECTION_YES
        data.extend(pack_uint16(direction))
    if len(data) <= 2:
        return bytearray()

    changed = bytearray()
    changed.extend(pack_uint8(i))
    changed.extend(data)
    return changed

def deserialise(data: bytes, i: int) -> Tuple[retVal, int]:
    changed = data[i]
    ret = retVal()
    i+=1
    if changed & ISID_YES:
        isid, i = unpack_uint16(data, i)
        ret.isid = isid
    else:
        raise ValueError("Missing InServerID")
    if changed & X_YES:
        x, i = unpack_int32(data, i)
        ret.x = x
    if changed & Y_YES:
        y, i = unpack_int32(data, i)
        ret.y = y
    if changed & STATE_YES:
        s, i = unpack_uint8(data, i)
        ret.state = s
    if changed & DIRECTION_YES:
        d, i = unpack_uint16(data, i)
        ret.direction = d
    return ret, i

def serialise_many(entities) -> bytes:
    send = bytearray()
    for e in entities:
        data = serialise(x=e.x,y=e.y,state=e.state, direction=e.direction,isid=e.isid)
        send.extend(data)
    return send

def deserialise_many(data:bytes):
    i = 0
    retVals: List[retVal] = []
    while i < len(data):
        deserialised, i = deserialise(data, i)
        retVals.append(deserialised)
    return retVals

        

if __name__ == "__main__":
    entities = []
    isid = 0

    for _ in range(randint(1, 10)):  # Ensure at least one entity is generated
        e = retVal()
        e.isid = isid
        isid += 1

        # Make sure at least one field is set besides isid
        has_data = False
        if randint(0, 1):
            e.x = randint(-12345, 12345)
            has_data = True
        if randint(0, 1):
            e.y = randint(-12345, 12345)
            has_data = True
        if randint(0, 1):
            e.state = randint(0, 4)
            has_data = True
        if randint(0, 1):
            e.direction = randint(0, 360)
            has_data = True

        # Ensure at least one attribute besides isid
        if not has_data:
            continue
            e.x = randint(-12345, 12345)  # Default to setting 'x'

        entities.append(e)

    serialised = serialise_many(entities)
    deserialised = deserialise_many(serialised)

    if entities == deserialised:
        print("All entities match after serialization and deserialization!")
    else:
        print("Mismatch found!")
        for orig, deser in zip(entities, deserialised):
            print(f"Original: {orig} | Deserialized: {deser}, noe: {len(entities)}, len bytes: {len(serialised)}, node: {len(deserialised)}")

