package src

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
)

// const IP_ADDR = "127.0.0.1"
const IP_ADDR = "192.168.0.5"

func bytesToUint16(b []byte) uint16 {
    return binary.BigEndian.Uint16(b)
}
func intToBytes(n int) []byte {
    // Create a byte slice with a length of 4 (for int32) or 8 (for int64)
    byteArray := make([]byte, 4)
    binary.BigEndian.PutUint32(byteArray, uint32(n))
    return byteArray
}
func encodeMessage(message string) ([]byte, error) {
    length := int32(len(message))
    buf := new(bytes.Buffer)

    // Write the length of the message (4 bytes)
    err := binary.Write(buf, binary.BigEndian, length)
    if err != nil {
        return nil, err
    }
    // fmt.Println(buf.Bytes()[:4])

    // Write the message itself
    buf.Write([]byte(message))
    // fmt.Println(buf.Bytes()[:4])

    return buf.Bytes(), nil
}
// decodeMessage decodes a length-prefixed message.

// Returns the message, a boolean indicating if more data is needed, the number of missing bytes, and an error if any.
func decodeMessage(data []byte) ([]byte, bool, int, error) {
    const lengthPrefixSize = 4

    if len(data) < lengthPrefixSize {
        // Not enough data to read the length prefix
        return nil, true, lengthPrefixSize - len(data), nil
    }

    buf := bytes.NewBuffer(data)

    // Read the length of the message (4 bytes)
    var length int32
    err := binary.Read(buf, binary.BigEndian, &length)
    if err != nil {
        return nil, false, 0, err
    }
    fmt.Printf("Expected Lenght of data: %v\n", length)

    totalLength := int(length) + lengthPrefixSize // Message length plus the 4 bytes of the length field
    // fmt.Println(int(length), lengthPrefixSize, totalLength)
    if len(data) < totalLength {
        // Not enough data to read the full message
        return nil, true, totalLength - len(data), nil
    }

    // Read the message itself
    message := make([]byte, length)

    // This coppies the message from fourth byte to the end
    // skips first four bytes (a.k.a. Lenght)
    _, err = io.ReadFull(buf, message)
    if err != nil {
        return nil, false, 0, err
    }
    return message, false, 0, nil
}

// DecodeMessage takes a slice of bytes and decodes it into a user ID and user data.
func decodeUDPMessage(data []byte) (uint16, []byte, error) {
	if len(data) < 2 {
		return 0, nil, fmt.Errorf("data too short, must be at least 2 bytes")
	}
	
	// Read the first 2 bytes as a uint16 user ID
	userID := binary.BigEndian.Uint16(data[:2])
	
	// The rest of the data is the user data
	userData := data[2:]
    // fmt.Println(userID, userData, data)
	
	return userID, userData, nil
}
