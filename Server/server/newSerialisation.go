package server

import (
	"bytes"
	"fmt"
    "encoding/binary"
)

const ISID_YES              = 0b00000001
const X_YES                 = 0b00000010
const Y_YES                 = 0b00000100
const STATE_YES             = 0b00001000
const DIRECTION_YES         = 0b00010000

func packInt32(value int32) []byte {
	buf := new(bytes.Buffer)
	err := binary.Write(buf, binary.BigEndian, value)
	if err != nil {
		fmt.Println("binary.Write(packInt32) failed:", err)
	}
	return buf.Bytes()
}
func packUint32(value uint32) []byte {
	buf := new(bytes.Buffer)
	err := binary.Write(buf, binary.BigEndian, value)
	if err != nil {
		fmt.Println("binary.Write(packUint32) failed:", err)
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
func unpackUint32(data []byte, offset int) (uint32, int, error) {
	var value uint32

	buf := bytes.NewReader(data[offset:])
	err := binary.Read(buf, binary.BigEndian, &value)
	if err != nil {
		return 0, offset, fmt.Errorf("binary.Read(unpackUint32) failed: %w", err)
	}
	return value, offset + 4, nil

}

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

type Change[T any] struct  {
    Changed         bool
    Value           T
}

type SerialisationEntityStruct struct {
    InServerID      uint16
    X               Change[int32]
    Y               Change[int32]
    State           Change[uint8]
    Direction       Change[uint16]
}
func NewSerialisationEntityStruct(isid uint16, x int32, y int32, state uint8, dir uint16) *SerialisationEntityStruct {
    e := &SerialisationEntityStruct{}
    e.InServerID = isid
    e.X = Change[int32] {true, x}
    e.Y = Change[int32] {true, y}
    e.State = Change[uint8] {true, state}
    e.Direction = Change[uint16] {true, dir}
    return e
}

func Serialise(es *SerialisationEntityStruct) ([]byte, error) {
    var data bytes.Buffer
    var i int = 0

    i |= ISID_YES
    if _, err := data.Write(packUint16(es.InServerID)); err != nil {
        fmt.Println(err)
        return nil,err
    }
    if es.X.Changed {
        if _, err := data.Write(packInt32(es.X.Value)); err != nil {
            fmt.Println(err)
            return nil,err
        } else {
            i |= X_YES
        }
    }
    if es.Y.Changed {
        if _, err := data.Write(packInt32(es.Y.Value)); err != nil {
            fmt.Println(err)
            return nil,err
        } else {
            i |= Y_YES
        }
    }
    if es.State.Changed {
        if _, err := data.Write(packUint8(es.State.Value)); err != nil {
            fmt.Println(err)
            return nil,err
        } else {
            i |= STATE_YES
        }
    }
    if es.Direction.Changed {
        if _, err := data.Write(packUint16(es.Direction.Value)); err != nil {
            fmt.Println(err)
            return nil,err
        } else {
            i |= DIRECTION_YES
        }
    }
    if data.Len() <= 2 {
        return nil, fmt.Errorf("insuffixent data provided/entity not updated")
    }
    finalData := bytes.Buffer{}
	if err := finalData.WriteByte(byte(i)); err != nil {
		return nil, err
	}
    finalData.Write(data.Bytes())
    return finalData.Bytes(), nil
}
func SerialiseMany(es []*SerialisationEntityStruct) ([]byte, error) {
    var data bytes.Buffer
    for i, e := range es {
        if se, err := Serialise(e); err != nil {
            fmt.Printf("Failed to serialise entitiy %d, %v\n", i, err)
            continue
        } else {
            data.Write(se)
        }
    }
    if data.Len() == 0 {
        return nil, fmt.Errorf("No data serialised")
    }
    return data.Bytes(), nil
}

func Deserialise(data []byte, i int) (SerialisationEntityStruct, int, error) {
    var changed uint8
    var err error
    changed, i, err = unpackUint8(data, i)
    if err != nil {
        return SerialisationEntityStruct{}, -1, err
    }
    if changed & ISID_YES == 0 {
        return SerialisationEntityStruct{}, -1, fmt.Errorf("Missing in server id/data might be corrupted")
    }

    e := SerialisationEntityStruct{}
    isid, i, err  := unpackUint16(data, i)
    if err != nil {
        return SerialisationEntityStruct{}, -1, err
    }
    e.InServerID = isid

    if changed & X_YES != 0 {
        var x int32
        x, i, err = unpackInt32(data, i) 
        if err != nil {
            return SerialisationEntityStruct{}, -1, err
        }
        e.X.Changed = true
        e.X.Value = x
    }
    if changed & Y_YES != 0 {
        var y int32
        y, i, err = unpackInt32(data, i) 
        if err != nil {
            return SerialisationEntityStruct{}, -1, err
        }
        e.Y.Changed = true
        e.Y.Value = y
    }
    if changed & STATE_YES != 0 {
        var s uint8
        s, i, err = unpackUint8(data, i) 
        if err != nil {
            return SerialisationEntityStruct{}, -1, err
        }
        e.State.Changed = true
        e.State.Value = s
    }
    if changed & DIRECTION_YES != 0 {
        var d uint16
        d, i, err = unpackUint16(data, i) 
        if err != nil {
            return SerialisationEntityStruct{}, -1, err
        }
        e.Direction.Changed = true
        e.Direction.Value = d
    }

    return e, i, nil
}

func DeserialiseMany(data []byte, i int) ([]SerialisationEntityStruct, int, error) {
    entities := make([]SerialisationEntityStruct, 0)
    for i < len(data) {
        var e SerialisationEntityStruct
        var err error
        e, i, err = Deserialise(data, i)
        if err != nil {
            return nil, -1, err
        }
        entities = append(entities, e)
    }
    return entities, i, nil
}
