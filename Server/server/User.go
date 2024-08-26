package server

import (
	"fmt"
	"math"
	"net"
	"sync"
)

type Color struct {
    R, G, B uint8
}
var colors = []Color{
    {R: 255, G: 0, B: 0},    // Red
    {R: 0, G: 255, B: 0},    // Green
    {R: 0, G: 0, B: 255},    // Blue
    {R: 255, G: 255, B: 0},  // Yellow
    {R: 0, G: 255, B: 255},  // Cyan
    {R: 255, G: 0, B: 255},  // Magenta
    {R: 192, G: 192, B: 192},// Silver
    {R: 128, G: 128, B: 128},// Gray
    {R: 128, G: 0, B: 0},    // Maroon
    {R: 128, G: 128, B: 0},  // Olive
    {R: 0, G: 128, B: 0},    // Dark Green
    {R: 128, G: 0, B: 128},  // Purple
    {R: 0, G: 128, B: 128},  // Teal
    {R: 0, G: 0, B: 128},    // Navy
    {R: 255, G: 165, B: 0},  // Orange
    {R: 255, G: 192, B: 203},// Pink

}
type User struct {
    ID              int
    Name            string
    UserOn          bool

    GameAddr        *net.UDPAddr
    EventConn       *net.TCPConn
    Channel         chan []byte
    msgCount        uint32

    InServerID      uint16
    Entity          Entity
    Color           Color

    streamMutex     sync.Mutex
    gameMutex       sync.Mutex
    dataMutex       sync.Mutex
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
        Color: colors[id%len(colors)],
        UserOn: true,
        msgCount: 0,
    }
    u.Entity.InServerID = InServerID
    u.Entity.CurrentState = EntityState{
        Pos: Vector2{0,0},
        State: 0,
        Direction: 0,
        Health: 0,
    }
    return u
}

func (u *User)Close() {
    u.UserOn = false
    u.EventConn.Close()
    fmt.Printf("Closed TCP connection with client: %v\n", u.InServerID)
}


func (u *User) HandleGameData() {
    for {
		select {
		case buffer := <-u.Channel:
            pkgno, i, err := unpackUint32(buffer, 0)
            if err != nil {
                fmt.Println("Error in unpacking uint32", err)
                continue
            }
            // Handle uint32 overflow if packages too many
            if pkgno <= u.msgCount {
                continue
            }
            u.msgCount = pkgno
            deserData := buffer[i:]
            // xl := bytesToUint16(buffer[:2])
            e, _, err := Deserialise(deserData, 0)
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
