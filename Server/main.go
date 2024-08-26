package main

import (
	"fmt"
	"github.com/Tiziozero/entricity/Server/server"
)
var idCounter int = 0
// const LOCAL_PUBLIC_IP_ADDR = "0.0.0.0"
const LOCAL_PUBLIC_IP_ADDR = "192.168.0.5"

func main() {
    server := &server.Server{}
    if server.NewServer(LOCAL_PUBLIC_IP_ADDR, 10101, LOCAL_PUBLIC_IP_ADDR, 12345, 9999) != nil {
        fmt.Println("Failed to create server. Exiting...")
        return
    }
    defer server.Close()
}
