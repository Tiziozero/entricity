package main

import (
    "fmt"
    "github.com/Tiziozero/entricity/Server/src"
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


const LOCAL_PUBLIC_IP_ADDR = "192.168.0.5"

func main() {
    server := &src.Server{}
    if server.NewServer(LOCAL_PUBLIC_IP_ADDR, 10101, LOCAL_PUBLIC_IP_ADDR, 12345) != nil {
        fmt.Println("Failed to create server. Exiting...")
        return
    }
    go server.BroadcastGame()
    go server.GameListenerUDP()
    
    defer server.Close()

    server.HandleConns()
}
