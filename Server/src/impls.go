package src

import (
	"bytes"
	"encoding/binary"
    "math/rand"
	"fmt"
	"net"
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
func EncodeMessage(message string) ([]byte, error) {
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
func DecodeMessage(c *net.TCPConn, buffer []byte) ([]byte, error) {
    n, err := c.Read(buffer)
    var got int = n
    // int
    const lengthPrefixSize = 4

    if len(buffer) < lengthPrefixSize {
        // Not enough buffer to read the length prefix
        return nil, fmt.Errorf("Not enough data/data too short to decode")
    }

    buf := bytes.NewBuffer(buffer)

    // Read the length of the message (4 bytes)
    var length int32
    err = binary.Read(buf, binary.BigEndian, &length)
    if err != nil {
        return nil, err
    }
    //DEBUG
    fmt.Printf("Expected Lenght of buffer: %v\n", length)


    totalLength := int(length) + lengthPrefixSize // Message length plus the 4 bytes of the length field
    if len(buffer) < int(totalLength) {
        buffer = make([]byte, length)
    }

    for got < totalLength {
        // Not enough buffer to read the full message
        n, err := c.Read(buffer[n:])
        if err != nil || n == 0 {
            return nil, fmt.Errorf("User Disconnected")
        }
        got += n
    }
    fmt.Println(buffer[lengthPrefixSize:])
    return buffer[lengthPrefixSize:], nil
}
func DecodeLengthFromBytes(buffer []byte) (int, error) {
    buf := bytes.NewBuffer(buffer)
    var length int32
    err := binary.Read(buf, binary.BigEndian, &length)
    if err != nil {
        return -1, err
    }
    return int(length), nil
}
// DecodeMessage takes a slice of bytes and decodes it into a user ID and user data.
func DecodeUDPMessage(data []byte) (uint16, []byte, error) {
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

func GenerateRandomString(n int) string {
    letters := []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    s := make([]rune, n)
    for i := range s {
        s[i] = letters[rand.Intn(len(letters))]
    }
    return string(s)
}

func GenerateNewAccessToken() string {
    return GenerateRandomString(256)
}
