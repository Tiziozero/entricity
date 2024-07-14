package main

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net"
    "strconv"
	"time"
)

const IP_ADDR = "127.0.0.1"

func intToBytes(n int) []byte {
    // Create a byte slice with a length of 4 (for int32) or 8 (for int64)
    byteArray := make([]byte, 4)
    binary.BigEndian.PutUint32(byteArray, uint32(n))
    return byteArray
}
func (s *Server)NewServer(port string) {
    listener, err := net.Listen("tcp", port)
    if err != nil {
        fmt.Printf("Error can't create server: %v", err)
        return
    }
    s.listener = listener
    s.users =make(map[int]*User)
    addr := net.UDPAddr{
        Port: 12345,
        IP:   net.ParseIP(IP_ADDR),
    }

    conn, err := net.ListenUDP("udp", &addr)
    if err != nil {
        fmt.Println(err)
        return
    }
    s.gameListener = conn
}
func (s *Server) HandleConns() {
    for {
        // Wait for a connection.
        conn, err := s.listener.Accept()
        if err != nil {
            fmt.Println("Error accepting connection:", err)
            continue
        }

        tcpConn, ok := conn.(*net.TCPConn)
        if !ok {
            fmt.Println("Failed to assert type net.TCPConn")
            conn.Close()

            continue
        }

        go s.HandleUserRequest(tcpConn)
    }
}
type userRequestStruct struct {
    ID      int `json:"id"`
    Name    string `json:"name"`
}
type Vector2 struct {
    x       float64
    y       float64
}
func (v *Vector2)Normalize() Vector2 {
    h := math.Sqrt(v.x*v.x + v.y*v.y)
    if h == 0 {
        return Vector2{0,0}
    }
    return Vector2{v.x/h, v.y/h}
}
type UserData struct {
    ID      int
    Name    string
    Health  float32
    Pos     Vector2
}

func (s *Server)HandleUserRequest(conn *net.TCPConn) {
    idCounter++
    buffer := make([]byte, 1024)
    n, err := conn.Read(buffer)
    fmt.Println(buffer[:n])
    if err != nil {
        fmt.Println("HandleUserRequest Failed to read from user:", err)
        return
    }
    // Get User Request
    msg, _, _, err := decodeMessage(buffer[:n])
    userJson := userRequestStruct{}
    err = json.Unmarshal([]byte(msg), &userJson)
    if err != nil {
        fmt.Println("Failed to Unmarshal Json: ", err)
    }
    fmt.Println(userJson)
    
    // Create User
    id := userJson.ID
    u := NewUser(id, nil, conn)
    s.users[u.ID] = u
    
    //Send User ID Back (for now, implement actual connection method here)
    sid := strconv.Itoa(id)
    fmt.Println("string id: ",sid)
    b, err := encodeMessage(sid)
    if err != nil {
        fmt.Println(err)
        return
    }
    fmt.Println(string(b))
    conn.Write(b)
}
func NewUser(id int, addr *net.UDPAddr, conn *net.TCPConn) *User {
    u := &User{
        addr: addr,
        conn: conn,
        ID: id,
        channel: make(chan []byte, 1024),
        messageCounter: 0,
    }
    go u.HandleBuffer()
    go u.HandleConn()
    //go u.PrintMessageCount()
    
    return u
}

func (u *User) HandleConn() {
    fmt.Printf("Listening for messages from %v...\n", u.ID)
    buffer := make([]byte, 1024)
    tmp := make([]byte, 256)  
    for {
        userMsg := make([]byte, 0)
        n, err := u.conn.Read(buffer)
        userMsg, more, _, err := decodeMessage(buffer[:n])
        for more {
            buffer = append(buffer, tmp...)
            fmt.Printf("Buffer size now: %v\n", len(buffer))

            n2, err := u.conn.Read(buffer[n:])
            if err != nil {
                fmt.Println("HandleConn Failed to read from user:", err)
                return
            }
            n += n2
            userMsg, more, _, err = decodeMessage(buffer[:n])
        }
        if err != nil {
            fmt.Println("Failed to decode message:", err)
            return
        }
        // only message
        endMessage := string(buffer[4:])
        fmt.Printf("Received %v bytes: %v\n", len(userMsg), endMessage)
        fmt.Printf("\"%v\"\n", endMessage)

        msg, err := encodeMessage(string(userMsg) + " from server")
        if err != nil {
            fmt.Println("Failed to encode message:", err)
            return
        }

        _, err = u.conn.Write(msg)
        if err != nil {
            fmt.Println("Failed to write to user:", err)
            return
        }
    }
}

func (u *User) HandleBuffer() {
    for {
		select {
		case buffer := <-u.channel:
            // xl := bytesToUint16(buffer[:2])
			// fmt.Printf("User %d received message: %s\n", u.id, string(buffer))
			u.thisMessage = buffer
            u.messageCounter++
		}
	}
}
func (u *User) PrintMessageCount() {
    for {
        time.Sleep(10 * time.Second)
        fmt.Printf("User %d has received %d messages\n", u.ID, u.messageCounter)
    }

}


func encodeMessage(message string) ([]byte, error) {
    length := int32(len(message))
    buf := new(bytes.Buffer)

    // Write the length of the message (4 bytes)
    err := binary.Write(buf, binary.BigEndian, length)
    if err != nil {
        return nil, err
    }
    fmt.Println(buf.Bytes()[:4])

    // Write the message itself
    buf.Write([]byte(message))
    fmt.Println(buf.Bytes()[:4])

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
