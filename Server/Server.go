package main

import (
	"encoding/json"
	"fmt"
	"net"
    "sync"
    "google.golang.org/protobuf/proto"
    pb "github.com/Tiziozero/entricity/Server/protos/protos"
)


type Server struct {
    listener        net.Listener
    gameListener    *net.UDPConn
    users           map[uint16]*User
    mutex           sync.Mutex
    idCounter       int
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
        fmt.Println("Error in creating server:", err)
        return err
    }
    s.gameListener = conn
    return nil
}
func (s* Server)BroadcastGame() {
    data := make([]byte, 0)
    var err error = nil
    for {
        s.mutex.Lock()
        if len(s.users) > 0 {
            entities := []*pb.Entity{}
            for _, u := range s.users {
                u.dataMutex.Lock()
                e := &pb.Entity{
                    InServerId:    uint32(u.data.inServerID),
                    X:             float32(u.data.Pos.x),
                    Y:             float32(u.data.Pos.y),
                    AnimationIndex: u.data.AnimationIndex,

                    State:         u.data.State,
                    Direction:     u.data.Direction,

                }
                u.dataMutex.Unlock()
                entities = append(entities, e)
            }

            // add messages here
            // Create some example events
            events := []*pb.Event{
                {
                    EventType: "login",
                    EventData: "user1 logged in",
                },
                {
                    EventType: "logout",
                    EventData: "user2 logged out",
                },
            }


            // Create a message containing entities and events
            message := &pb.Message{
                Entities: entities,
                Events:   events,
            }
            data, err = proto.Marshal(message)
            if len(data) > 1024 {
                fmt.Println("WARNING - data is over 1024 bytes. to handle. len:", len(data))
            }
            if err != nil {
                fmt.Println("Error in serialising data to send to users:", err)
                continue
            }

            for _, u := range s.users {
                if u.userOn {
                    _, err = s.gameListener.WriteToUDP(data, u.addr)
                    // fmt.Println("sending data to:", u.addr)
                    if err != nil {
                        // fmt.Println("Error in sending data to user game conn:", err)
                    }
                } else {
                    delete(s.users, u.inServerID)
                    fmt.Printf("Deleted user: %v:%v\n", u.inServerID, u.ID)
                    fmt.Printf("Remaining users:")
                    for _,u := range s.users{
                        fmt.Println("\t",u)
                    }
                }
            }
        }
        s.mutex.Unlock()
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
type userCommunicationStruct struct {
    Type        string `json:"type"`
    Message     interface{} `json:"message"`
}

func respondWithError(conn *net.TCPConn, err error) {
    r := userCommunicationStruct{"error", err.Error()}
    respJsonBytes, err := json.Marshal(r)
    b, err := encodeMessage(string(respJsonBytes))
    if err != nil {
        fmt.Printf("Failed to write to user: %v", err)
        return
    }
    fmt.Println("Responding (with error) with:", string(b))
    conn.Write(b)

}

func (s *Server)HandleUserRequest(conn *net.TCPConn) {
    buffer := make([]byte, 1024)

    n, err := conn.Read(buffer)
    if err != nil {
        fmt.Println("HandleUserRequest Failed to read from user:", err)
        respondWithError(conn, err)
        return
    }

    // Get User Request
    msg, _, _, err := decodeMessage(buffer[:n])
    userJson := userCommunicationStruct{}
    err = json.Unmarshal([]byte(msg), &userJson)
    if err != nil {
        fmt.Println("Failed to Unmarshal Json: ", err)
        respondWithError(conn, err)
        return
    }

    // Create User
    messageMap, ok := userJson.Message.(map[string]interface{})
    if !ok {
        fmt.Println("Message is not a valid map")
        respondWithError(conn, fmt.Errorf("Failed to construct from response json"))
        return
    }
    id, ok := messageMap["id"].(float64) // JSON unmarshals numbers as float64
    if !ok {
        fmt.Println("ID is not a valid float64")
        respondWithError(conn, fmt.Errorf("Failed to construct from response json"))
        return
    }
    s.mutex.Lock()
    s.idCounter++
    if s.idCounter > 100 {
        s.idCounter = 0
    }
    u := NewUser(int(id), uint16(s.idCounter), nil, conn)
    s.users[u.inServerID] = u
    
    // Respond with in server id
    resp := struct{
        ID      int `json:"in_server_id"`
    }{ s.idCounter }
    defer s.mutex.Unlock()
    respJsonBytes, err := json.Marshal(resp)
    b, err := encodeMessage(string(respJsonBytes))
    if err != nil {
        fmt.Println("Error in encoding message:",err)
        respondWithError(conn, err)
        return
    }

    conn.Write(b)
}
