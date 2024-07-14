package main

import (
	"encoding/binary"
	"fmt"
	"net"

)

var idCounter int = 0

func bytesToUint16(b []byte) uint16 {
    return binary.BigEndian.Uint16(b)
}

type User struct {
    addr        *net.UDPAddr
    conn        *net.TCPConn
    ID          int
    channel     chan []byte
    thisMessage []byte
    messageCounter int
}

type Server struct {
    listener        net.Listener
    gameListener    *net.UDPConn
    users           map[int]*User
}


func main() {
    server := Server{}
    server.NewServer(IP_ADDR+":10101")
    
    defer server.gameListener.Close()
    defer server.listener.Close()

    buffLen := 1024
    buffer := make([]byte, buffLen)
    go func(s *Server){
        for {
            // Read the initial part of the message
            n, remoteAddr, err := server.gameListener.ReadFromUDP(buffer)
            if err != nil {
                fmt.Println(err)
                continue
            }
            id := int(bytesToUint16(buffer[:2]))
            // remoteAddrStr := remoteAddr.String()
            u, exists := server.users[id]
            if !exists {
                fmt.Printf("Unauthorised user: %v\n", remoteAddr.String())
            }
            if u.addr == nil {
                u.addr = remoteAddr
            }
            select {
            case u.channel <- buffer[:n]:
            default:
                fmt.Printf("User %d channel is full, dropping message\n", u.ID)
            }
        }
    }(&server)
    server.HandleConns()
}

