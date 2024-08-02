package src

import "fmt"

const TEST_PORT_UDP = "127.0.0.1:3021"
const TEST_PORT_TCP = "127.0.0.1:3020"

var s * Server
func test() int { 
    return -1
    s = &Server{}
    s.NewServer("127.0.0.1", 3020, "127.0.0.1", 3021)
    return 0
}

func test_udp() int {
    go s.HandleConns()
    go s.BroadcastGame()
    fmt.Printf("Listening at tcp:%v, udp:%v", TEST_PORT_TCP, TEST_PORT_UDP)
    s.GameListenerUDP()
    return 0
}
