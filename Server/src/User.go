package src

import (
	"encoding/json"
	"fmt"
	"math"
	"net"
	"sync"
)
type User struct {
    GameAddr        *net.UDPAddr
    EventConn       *net.TCPConn
    ID              int
    Name            string
    InServerID      uint16
    Channel         chan []byte
    Entity          Entity
    UserOn          bool
    streamMutex     sync.Mutex
    gameMutex       sync.Mutex
    dataMutex       sync.Mutex
}
type Entity struct {
    InServerID      uint16
    CurrentState    EntityData
    LastState       EntityData
}
type EntityData struct {
    Pos             Vector2
    State           uint8
    AnimationIndex  uint32
    Direction       uint8
    Health          int
}

type Vector2 struct {
    x       int32
    y       int32
}
func (v *Vector2)Normalize() Vector2 {
    h := math.Sqrt(float64(v.x*v.x + v.y*v.y))
    if h == 0.0 {
        return Vector2{0,0}
    }
    return Vector2{int32(float64(v.x)/h), int32(float64(v.y)/h)}
}

func NewUser(id int, InServerID uint16, EventAddr *net.UDPAddr, EventConn *net.TCPConn) *User {
    u := &User{
        GameAddr: EventAddr,
        EventConn: EventConn,
        ID: id,
        InServerID: InServerID,
        Channel: make(chan []byte, 1024),
        UserOn: true,
    }
    u.Entity.InServerID = InServerID
    u.Entity.CurrentState = EntityData{
        Pos: Vector2{0,0},
        State: 0,
        Direction: 0,
        Health: 0,
        AnimationIndex: 0,
    }
    return u
}

func (u *User)Close() {
    u.UserOn = false
    u.EventConn.Close()
    fmt.Printf("Closed TCP connection with client: %v\n", u.InServerID)
}

func (u *User) HandleEventMessages() {
    fmt.Printf("Listening for messages from %v...\n", u.ID)
    buffer := make([]byte, 1024)
    tmp := make([]byte, 256)  
    for {
        if ! u.UserOn {
            fmt.Println("User not on")
            break
        } else {
            fmt.Printf("User on: %v\n", u.UserOn)
        }
        userMsg := make([]byte, 0)
        u.streamMutex.Lock()
        n, err := u.EventConn.Read(buffer)
        if n <= 0 {
            u.Close()
            break
        }
        userMsg, more, rem, err := decodeMessage(buffer[:n])
        for more {
            fmt.Printf("Expecting %v more bytes\n", rem)
            buffer = append(buffer, tmp...)
            fmt.Printf("Buffer size now: %v\n", len(buffer))

            n2, err := u.EventConn.Read(buffer[n:])
            if err != nil {
                fmt.Println("HandleEventMessages Failed to read from user:", err)
                u.Close()
                break
            }
            n += n2
            userMsg, more, _, err = decodeMessage(buffer[:n])
        }
        // fmt.Printf("Got Full message of: %v bytes\n", len(userMsg))

        if err != nil {
            fmt.Println("Failed to decode message:", err)
            u.Close()
            break
        }
        // only message
        // endMessage := string(buffer[4:])
        // fmt.Printf("Received %v bytes: %v\n", len(userMsg), endMessage)
        type userEvent struct {
            Type string `json:"type"`
            Message string `json:"message"`
        }
        ue := userEvent{}
        err = json.Unmarshal(userMsg, &ue)
        if err != nil {
            fmt.Println("Error in unmarshalling user event:", err, "\n\n", userMsg)
            respondWithError(u.EventConn, err)
            continue
        }
        if ue.Message == "quit" {
            u.Close()
            break
        }

        msg, err := encodeMessage(string(userMsg) + " from server")
        if err != nil {
            fmt.Println("Failed to encode message:", err)
            u.Close()
            break
        }

        // fmt.Printf("Responding with %v\n", msg)
        _, err = u.EventConn.Write(msg)
        if err != nil {
            fmt.Println("Failed to write to user:", err)
            u.Close()
            break
        }
        u.streamMutex.Unlock()
    }
    fmt.Println("Broke out of get loop", u.UserOn)
}

func (u *User) HandleGameData() {
    for {
		select {
		case buffer := <-u.Channel:
            // xl := bytesToUint16(buffer[:2])
            e, err := Deserialise(buffer)
            if err != nil {
                fmt.Printf("Failed to deserialize entity: %v", err)
                continue
            }
            u.dataMutex.Lock()
            // fmt.Printf("Deserialized entity: %+v\n", deserializedEntity)
            if e.X.Changed {
                u.Entity.CurrentState.Pos.x = e.X.Value
            }
            if e.Y.Changed {
                u.Entity.CurrentState.Pos.y = e.Y.Value
            }
            if e.State.Changed {
                u.Entity.CurrentState.State = e.State.Value
            }
            if e.Direction.Changed {
                u.Entity.CurrentState.Direction = e.Direction.Value
            }
            u.dataMutex.Unlock()
		}
	}
}
