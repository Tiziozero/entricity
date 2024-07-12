package main

import (
    "encoding/binary"
    "fmt"
    "net"
    "time"
)

var idCounter int = 0

func bytesToUint16(b []byte) uint16 {
    return binary.BigEndian.Uint16(b)
}

type User struct {
    addr        *net.UDPAddr
    id          int
    channel     chan []byte
    thisMessage []byte
    messageCounter int
}

func (u *User) HandleBuffer() {
    for {
		select {
		case buffer := <-u.channel:
            // xl := bytesToUint16(buffer[:2])
			// fmt.Printf("User %d received message: %s\n", u.id, string(buffer))
			u.thisMessage = buffer
            u.messageCounter++
			// Further processing can be done here
		}
	}
}
func (u *User) PrintMessageCount() {
    for {
        time.Sleep(10 * time.Second)
        fmt.Printf("User %d has received %d messages\n", u.id, u.messageCounter)
    }

}

func NewUser(addr *net.UDPAddr) *User {
    idCounter++
    u := &User{
        addr: addr,
        id: idCounter,
        channel: make(chan []byte, 1024),
        messageCounter: 0,
    }
    go u.HandleBuffer()
    go u. PrintMessageCount()
    
    return u
}

type Users struct {
    Users map[string]*User
}

func main() {
    users := Users{
        Users: make(map[string]*User),
    }
    addr := net.UDPAddr{
        Port: 12345,
        IP:   net.ParseIP("0.0.0.0"),
    }

    conn, err := net.ListenUDP("udp", &addr)
    if err != nil {
        fmt.Println(err)
        return
    }
    defer conn.Close()

    buffLen := 1024
    buffer := make([]byte, buffLen)

    for {
        // Read the initial part of the message
        n, remoteAddr, err := conn.ReadFromUDP(buffer)
        if err != nil {
            fmt.Println(err)
            continue
        }

        remoteAddrStr := remoteAddr.String()
        u, exists := users.Users[remoteAddrStr]
        if !exists {
            u = NewUser(remoteAddr)
            users.Users[remoteAddrStr] = u
        }
        select {
		case u.channel <- buffer[:n]:
		default:
			fmt.Printf("User %d channel is full, dropping message\n", u.id)
		}
    }
}

