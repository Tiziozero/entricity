package src

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"math/rand"
)

type Change[T any] struct  {
    Changed         bool
    Value           T
}

type SerialisationEntityStruct struct {
    InServerID      uint16
    X               Change[int32]
    Y               Change[int32]
    State           Change[uint8]
    Direction       Change[uint8]
}

func packInt32(value int32) []byte {
	buf := new(bytes.Buffer)
	err := binary.Write(buf, binary.BigEndian, value)
	if err != nil {
		fmt.Println("binary.Write(packInt32) failed:", err)
	}
	return buf.Bytes()
}

func packUint16(value uint16) []byte {
	buf := new(bytes.Buffer)
	err := binary.Write(buf, binary.BigEndian, value)
	if err != nil {
		fmt.Println("binary.Write(packInt16) failed:", err)
	}
	return buf.Bytes()
}

func packUint8(value uint8) []byte {
	buf := new(bytes.Buffer)
	err := binary.Write(buf, binary.BigEndian, value)
	if err != nil {
		fmt.Println("binary.Write(packInt8) failed:", err)
	}
	return buf.Bytes()
}

// Function to unpack an int32 value from a byte slice with a given offset
func unpackInt32(data []byte, offset int) (int32, int, error) {
	var value int32

	buf := bytes.NewReader(data[offset:])
	err := binary.Read(buf, binary.BigEndian, &value)
	if err != nil {
		return 0, offset, fmt.Errorf("binary.Read(unpackInt32) failed: %w", err)

	}
	return value, offset + 4, nil

}


// Function to unpack a uint16 value from a byte slice with a given offset
func unpackUint16(data []byte, offset int) (uint16, int, error) {

	var value uint16
	buf := bytes.NewReader(data[offset:])
	err := binary.Read(buf, binary.BigEndian, &value)
	if err != nil {
		return 0, offset, fmt.Errorf("binary.Read(unpackInt16) failed: %w", err)
	}
	return value, offset + 2, nil
}

func unpackUint8(data []byte, offset int) (uint8, int, error) {
	var value uint8
	buf := bytes.NewReader(data[offset:])
	err := binary.Read(buf, binary.BigEndian, &value)
	if err != nil {
		fmt.Println("binary.Read failed:", err)
		return 0, offset, fmt.Errorf("binary.Read(unpackInt8) failed: %w", err)
	}
	return value, offset + 1, nil
}

// Returns empty array if everything fails or entity did not change
// Does not include inServerID
func serialise(e *SerialisationEntityStruct) []byte {
	data := new(bytes.Buffer) 

	if e.X.Changed {
		data.WriteByte(0x01)
		data.Write(packInt32(int32(e.X.Value)))
	}

	if e.Y.Changed {
		data.WriteByte(0x02)
		data.Write(packInt32(int32(e.Y.Value)))
	}

	if e.State.Changed {
		data.WriteByte(0x03)
		data.Write(packUint8(e.State.Value))
	}

	if e.Direction.Changed {
		data.WriteByte(0x04)
		data.Write(packUint8(e.Direction.Value))
	}

	return data.Bytes()
}
// returns an empty array if it failes completly
// doesn't include entities that fail to serialise
func SerialiseEntities(es []*SerialisationEntityStruct) []byte {
	data := new(bytes.Buffer)
    entitiesLength := len(es)
    length := packUint8(uint8(entitiesLength))
    data.Write(length)

    totalEntitiesWritten := 0
    for _,e := range es {
        entityData := new(bytes.Buffer)

        inServerID := packUint16(e.InServerID)
        // one byte
        entityData.WriteByte(0x00)
        // 2 bytes
        entityData.Write(inServerID)

        if entityData.Len() < 3 {
            fmt.Println("Failed to serialise Entity inServerID")
            continue
        }

        serialisedEntityData := serialise(e)
        if len(serialisedEntityData) <= 0 {
            fmt.Println("Failed to serialise Entity/Entity might not have changed")
            continue
        }
        entityData.Write(serialisedEntityData)
        // Should be greater than three / 1 for 0x00, one for in server id and 1+ from entity serialisation
        if entityData.Len() <= 3 {
            fmt.Println("Failed to serialise Entity")
            continue
        } else {
            data.Write(entityData.Bytes())
            totalEntitiesWritten ++
        }
    }
    // fmt.Printf("Serialised a total of %v out of %v entities. len data: %v\n", totalEntitiesWritten, length, data.Len())
    return data.Bytes()
}

// Returns 
func Deserialise(data []byte) (*SerialisationEntityStruct, error) {
    // ignoring health for now
    e := SerialisationEntityStruct{
        0,
        Change[int32]   {false, 0},
        Change[int32]   {false, 0},
        Change[uint8]   {false, 0},
        Change[uint8]   {false, 0},
    }
    i := 0
    if data[i] != 0x00 {
        fmt.Printf("Invalid fieldCode %v. first byte should be 0x00 followed by inServerID\n", string(data[i]))
        return nil, fmt.Errorf("Invalid fieldCode %v. first byte should be 0x00 followed by inServerID\n", string(data[i]))
    }
    i++

    var err error
    e.InServerID, i, err = unpackUint16(data, i)
    if err != nil {
        fmt.Printf("Fialed to deserialise inServerID/Invalid inServerID: %v.")
        return nil,fmt.Errorf("Fialed to deserialise inServerID/Invalid inServerID: %v.")
    }

    for i < len(data) {
        fieldCode := data[i]
        i++
        err = nil

        switch fieldCode {
        case 0x01:
            e.X.Value, i, err = unpackInt32(data, i)
            if err != nil {
                fmt.Println("Failed to deserialise Entity x position:", err)
            } else {
                e.X.Changed = true
            }
        case 0x02:
            e.Y.Value, i, err = unpackInt32(data, i)
            if err != nil {
                fmt.Println("Failed to deserialise Entity y position:", err)
            } else {
                e.Y.Changed = true
            }
        case 0x03:
            e.State.Value, i, err = unpackUint8(data, i)
            if err != nil {
                fmt.Println("Failed to deserialise Entity state:", err)
            } else {
                e.State.Changed = true
            }
        case 0x04:
            e.Direction.Value, i, err = unpackUint8(data, i)
            if err != nil {
                fmt.Println("Failed to deserialise Entity direction:", err)
            } else {
                e.Direction.Changed = true
            }
        default:
            i--
            fmt.Println("Invalid Field Code at: %v", i)
                return nil, fmt.Errorf(
                    "Invalid Field Code at: %v. %v", i,
                    "This will cause the rest of the data to not be valid.")
        }
    }
    return &e, nil
}

func DeserialiseEntityFrom(data []byte, i int) (*SerialisationEntityStruct, int, error) {
    // ignoring health for now
    e := SerialisationEntityStruct{
        0,
        Change[int32]   {false, 0},
        Change[int32]   {false, 0},
        Change[uint8]   {false, 0},
        Change[uint8]   {false, 0},
    }

    if i >= len(data) {
        return nil, i, fmt.Errorf("data index out of range")
    }

    fieldCode := data[i]
    i++
    if fieldCode != 0x00 {
        return nil, i, fmt.Errorf("invalid field code. expected 0x00, got %x", fieldCode)
    }

    var err error
    e.InServerID, i, err = unpackUint16(data, i)
    if err != nil {
        return nil, i, fmt.Errorf("failed to deserialise InServerID: %w", err)
    }

loop:
    for i < len(data) {
        fieldCode = data[i]
        i++
        switch fieldCode {
        case 0x01:
            e.X.Value, i, err = unpackInt32(data, i)
            if err != nil {
                fmt.Println("Failed to unpack X position:", err)
            } else {
                e.X.Changed = true
            }
        case 0x02:
            e.Y.Value, i, err = unpackInt32(data, i)
            if err != nil {
                fmt.Println("Failed to unpack Y position:", err)
            } else {
                e.Y.Changed = true
            }
        case 0x03:
            e.State.Value, i, err = unpackUint8(data, i)
            if err != nil {
                fmt.Println("Failed to unpack State:", err)
            } else {
                e.State.Changed = true
            }
        case 0x04:
            e.Direction.Value, i, err = unpackUint8(data, i)

            if err != nil {

                fmt.Println("Failed to unpack Direction:", err)
            } else {
                e.Direction.Changed = true
            }
        case 0x00:
            i--
            break loop
        default:
            return &e, i, fmt.Errorf("unknown field code: %x", fieldCode)

        }
    }
    
    return &e, i, nil
}

func DeserialiseEntities(data []byte) ([]*SerialisationEntityStruct, error) {
    i := 0
    entitiesLength, i, err := unpackUint8(data, i)
    if err != nil{
        fmt.Printf("Failed to decode length: %v", err)
        return nil, fmt.Errorf("Failed to decode length")
    }
    
    entities := make([]*SerialisationEntityStruct, entitiesLength)
    entitiesIndex := 0

    for i < len(data) && entitiesIndex < int(entitiesLength) {
        fieldCode := data[i]
        if fieldCode != 0x00 {
            fmt.Println("invalid fieldCode")
            return nil, fmt.Errorf("invalid fieldCode")
        }
        var entity *SerialisationEntityStruct
        entity, i, err = DeserialiseEntityFrom(data, i)
        if err != nil {
            fmt.Println("Error deserialising entity:", err)
            return entities[:entitiesIndex], fmt.Errorf(
                "Failed to deserialise entity%v. Returning successful entities. %v",
                err, "Data read from here on might be invalid. Therefore skipping.",
                )
        }
        // fmt.Printf("Deserialised entity: %v\n", entity.InServerID)
        entities[entitiesIndex] = entity
        entitiesIndex++
    }
    // fmt.Printf("Deserialised %v out of %v entities:", entitiesIndex, entitiesLength)
    return entities[:entitiesIndex], nil
}



// test main
func NewSerialisationEntityStruct(isid uint16, x int32, y int32, state uint8, dir uint8) *SerialisationEntityStruct {
    e := &SerialisationEntityStruct{}
    e.InServerID = isid
    e.X = Change[int32] {true, x}
    e.Y = Change[int32] {true, y}
    e.State = Change[uint8] {true, state}
    e.Direction = Change[uint8] {true, dir}
    return e
}
func NSES(isid uint16, x int32, y int32, state uint8, dir uint8) *SerialisationEntityStruct {
    e := &SerialisationEntityStruct{}
    e.InServerID = isid
    e.X = Change[int32] {true, x}
    e.Y = Change[int32] {true, y}
    e.State = Change[uint8] {true, state}
    e.Direction = Change[uint8] {true, dir}
    return e
}

func PrintSESs(es []*SerialisationEntityStruct, msg string) {
    if msg == "" {
        for _, e := range es {
            fmt.Printf("Entity: %v@%v:%v(s:%v;d:%v)\n", e.InServerID, e.X.Value, e.Y.Value, e.State.Value, e.Direction.Value)
        }
        return
    }
    fmt.Println(msg)
    for _, e := range es {
        fmt.Printf("\tEntity: %v@%v:%v(s:%v;d:%v)\n", e.InServerID, e.X.Value, e.Y.Value, e.State.Value, e.Direction.Value)
    }
}


// randint generates a random integer between a and b (inclusive)
func randint(a, b int) int {
    return rand.Intn(b-a+1) + a
}

func TestSingleEntity() {
    errors := make([]error, 0)
    // Creation
    testEntity := NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40)))
    PrintSESs([]*SerialisationEntityStruct{testEntity}, "testEntity:")

    // Serialisation
    serialisedTestEntity := new(bytes.Buffer) 
    serialisedTestEntity.WriteByte(0x00)
    serialisedTestEntity.Write(packUint16(testEntity.InServerID))
    serialisedTestEntity.Write(serialise(testEntity))
        // to test if new entity
    serialisedTestEntity.WriteByte(0x00)

    deserialisedTestEntity, _, err := DeserialiseEntityFrom(serialisedTestEntity.Bytes(), 0)
    if err != nil {
        fmt.Printf("Failed to deserialise testEntity: %v\n", err)
        errors = append(errors, fmt.Errorf("Failed to deserialise testEntity: %v\n", err))
    } else {
    // Test
        // if success
        if testEntity.X.Value == deserialisedTestEntity.X.Value &&
        testEntity.Y.Value == deserialisedTestEntity.Y.Value &&
        testEntity.State.Value == deserialisedTestEntity.State.Value &&
        testEntity.Direction.Value == deserialisedTestEntity.Direction.Value {
            fmt.Println("Entities are the same. success.")
        } else {
            PrintSESs([]*SerialisationEntityStruct{deserialisedTestEntity},
            "Test failed. Deserialised testEntity:")
        }
    }
}

func TestMultipleEntities() {
    errors := make([]error, 0)
    // Creation
    testEntities := []*SerialisationEntityStruct{
        NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40))),
        NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40))),
        NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40))),
        NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40))),
        NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40))),
        NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40))),
        NSES(uint16(randint(0,1234)), int32(randint(0,12345)), int32(randint(0,12345)),uint8(randint(0,40)), uint8(randint(0,40))),
    }
    PrintSESs(testEntities, "testEntities:")
    // Serialisation
    serialisedTestEntities := SerialiseEntities(testEntities)
    deserialisedTestEntities, err := DeserialiseEntities(serialisedTestEntities)
    if err != nil {
        fmt.Printf("Failed to deserialise testEntities: %v\n", err)
        errors = append(errors, fmt.Errorf("Failed to deserialise testEntities: %v\n", err))
    }
    // Test
    if len(deserialisedTestEntities) != len(testEntities) {
        fmt.Printf("Entities length is not the same: testEntities: %v; deserialisedTestEntities: %v",
            len(testEntities), len(deserialisedTestEntities))
    } else {
        // if success
        errs := 0
        for i := 0; i < len(deserialisedTestEntities); i++ {
            testEntity := testEntities[i]
            deserialisedTestEntity := deserialisedTestEntities[i]
            if      testEntity.X.Value != deserialisedTestEntity.X.Value     ||
                    testEntity.Y.Value != deserialisedTestEntity.Y.Value     ||
                testEntity.State.Value != deserialisedTestEntity.State.Value ||
            testEntity.Direction.Value != deserialisedTestEntity.Direction.Value {
                fmt.Println("Entities at %v aren't the same. %v:%v\n", i, testEntities[i], deserialisedTestEntities[i])
                errs += 1
            }
        }
        if errs != 0 {
            fmt.Printf("%v entities aren't the same.\n", errs)
            PrintSESs(deserialisedTestEntities, "DeserialiseEntities:")
        } else {
            fmt.Println("All entities are the same. success")
        }
    }
}
