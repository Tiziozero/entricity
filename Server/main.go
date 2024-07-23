package main

import (
	"fmt"
)

/*
!!! -> https://protobuf.dev/reference/go/go-generated/#package
to generate protos:
---
I_PATH=../.
GO_OUT_PATH=./protos

protoc -I=$I_PATH \

    --go_out=$GO_OUT_PATH \
    entity.proto
---
*/

var idCounter int = 0


func main() {
    server := &Server{}
    if server.NewServer(IP_ADDR+":10101") != nil {
        fmt.Println("Failed to create server. Exiting...")
        return
    }
    
    defer server.Close()

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
            id, msg, err := decodeUDPMessage(buffer[:n])
            if err != nil {
                fmt.Println("In receiving data from user:", err)
                continue
            }
            // remoteAddrStr := remoteAddr.String()
            u, exists := server.users[id]
            if !exists {
                fmt.Printf("Unauthorised user %v: %v.\n", id, remoteAddr.String())
                fmt.Print("In server ids\n\t")
                for _, u := range server.users {
                    fmt.Print(",", u.inChannelID)
                }
                fmt.Println()
                continue
            }
            if u.addr == nil {
                u.addr = remoteAddr
            }
            select {
            case u.channel <- msg:
            default:
                fmt.Printf("User %d channel is full, dropping message\n", u.ID)
            }
        }
    }(server)
    go server.BroadcastGame()
    server.HandleConns()
}

