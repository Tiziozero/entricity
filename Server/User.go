package main

import (
	"fmt"
	"math"
	"net"
	"time"
    "google.golang.org/protobuf/proto"
    pb "github.com/Tiziozero/entricity/Server/protos/protos"
)
type User struct {
    addr        *net.UDPAddr
    conn        *net.TCPConn
    ID          int
    inChannelID uint16
    channel     chan []byte
    thisMessage []byte
    messageCounter int
    data        UserData
}
type UserData struct {
    ID              int
    Name            string
    Health          float32
    Pos             Vector2
    AnimationIndex  uint32
    State           uint32
    Direction       uint32
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

func NewUser(id int, inChannelID uint16, addr *net.UDPAddr, conn *net.TCPConn) *User {
    u := &User{
        addr: addr,
        conn: conn,
        ID: id,
        inChannelID: inChannelID,
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
            u.messageCounter++
            deserializedEntity := &pb.Entity{}
            err := proto.Unmarshal(buffer, deserializedEntity)
            if err != nil {
                fmt.Printf("Failed to deserialize entity: %v", err)
            }
            fmt.Printf("Deserialized entity: %+v\n", deserializedEntity)
            u.data.Pos.x = float64(deserializedEntity.GetX())
            u.data.Pos.y = float64(deserializedEntity.GetY())
            u.data.State = uint32(deserializedEntity.GetState())
            u.data.Direction = uint32(deserializedEntity.GetDirection())
            u.data.AnimationIndex = uint32(deserializedEntity.GetAnimationIndex())
		}
	}
}
func (u *User) PrintMessageCount() {
    for {
        time.Sleep(10 * time.Second)
        fmt.Printf("User %d has received %d messages\n", u.ID, u.messageCounter)
    }

}
