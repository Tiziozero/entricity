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
    if test() == 0{
        test_udp()
    }

    server := &Server{}
    if server.NewServer(IP_ADDR, 10101, IP_ADDR, 12345) != nil {
        fmt.Println("Failed to create server. Exiting...")
        return
    }
    go server.BroadcastGame()
    go server.gameListenerUDP()
    
    defer server.Close()

    server.HandleConns()
}
