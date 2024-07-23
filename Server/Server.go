package main

import (
	"encoding/json"
	"fmt"
	"net"
    "google.golang.org/protobuf/proto"
    pb "github.com/Tiziozero/entricity/Server/protos/protos"
)


type Server struct {
    listener        net.Listener
    gameListener    *net.UDPConn
    users           map[uint16]*User
}

func (s *Server)Close() {
    s.gameListener.Close()
    s.listener.Close()
}

func (s *Server)NewServer(port string) error {
    listener, err := net.Listen("tcp", port)
    if err != nil {
        fmt.Printf("Error can't create server: %v", err)
        return err
    }
    s.listener = listener
    s.users =make(map[uint16]*User)
    addr := net.UDPAddr{
        Port: 12345,
        IP:   net.ParseIP(IP_ADDR),
    }

    conn, err := net.ListenUDP("udp", &addr)
    if err != nil {
        fmt.Println(err)
        return err
    }
    s.gameListener = conn
    return nil
}
func (s* Server)BroadcastGame() {
    data := make([]byte, 0)
    var err error = nil
    for {
        if len(s.users) > 0 {
            entities := &pb.Entities{}
            for _, u := range s.users {
                e := &pb.Entity{
                    InServerId: uint32(u.inChannelID),
                    X: float32(u.data.Pos.x),
                    Y: float32(u.data.Pos.y),
                    AnimationIndex: u.data.AnimationIndex,
                    State: u.data.State,
                    Direction: u.data.Direction,
                }
                entities.Entities = append(entities.Entities, e)
            }
            data, err = proto.Marshal(entities)
            if err != nil {
                fmt.Println("Error in serialising data to send to users:", err)
                continue
            }
            for _, u := range s.users {
                _, err = s.gameListener.WriteToUDP(data, u.addr)
                fmt.Println("sending data to:", u.addr)
                if err != nil {
                    fmt.Println("Error in sending data to user game conn:", err)
                }
            }
        }
    }

}
func (s *Server) HandleConns() {
    for {
        // Wait for a connection.
        conn, err := s.listener.Accept()
        if err != nil {
            fmt.Println("Error accepting connection:", err)
            continue
        }

        tcpConn, ok := conn.(*net.TCPConn)
        if !ok {
            fmt.Println("Failed to assert type net.TCPConn")
            conn.Close()

            continue
        }

        go s.HandleUserRequest(tcpConn)
    }
}
type userRequestStruct struct {
    ID      int `json:"id"`
    Name    string `json:"name"`
}

func (s *Server)HandleUserRequest(conn *net.TCPConn) {
    idCounter++
    if idCounter > 100 {
        idCounter = 0
    }
    buffer := make([]byte, 1024)
    n, err := conn.Read(buffer)
    fmt.Println(buffer[:n])
    if err != nil {
        fmt.Println("HandleUserRequest Failed to read from user:", err)
        return
    }
    // Get User Request
    msg, _, _, err := decodeMessage(buffer[:n])
    userJson := userRequestStruct{}
    err = json.Unmarshal([]byte(msg), &userJson)
    if err != nil {
        fmt.Println("Failed to Unmarshal Json: ", err)
    }
    fmt.Println(userJson)
    
    // Create User
    id := userJson.ID
    u := NewUser(id, uint16(idCounter), nil, conn)
    s.users[u.inChannelID] = u
    
    resp := struct{
        ID      int `json:"in_server_id"`
    }{ idCounter }
    respJsonBytes, err := json.Marshal(resp)
    b, err := encodeMessage(string(respJsonBytes))
    if err != nil {
        fmt.Println(err)
        return
    }
    fmt.Println(string(b))
    conn.Write(b)
}
