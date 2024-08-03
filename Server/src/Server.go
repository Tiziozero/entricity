package src

import (
	"encoding/json"
	"fmt"
	"net"
	"sync"
)


type Server struct {
    listener        net.Listener
    gameListener    *net.UDPConn
    users           map[uint16]*User
    listenerMutex   sync.Mutex
    gameMutex       sync.Mutex
    userMutex       sync.Mutex
    idCounter       int
    serverOn        bool
}

func (s *Server)Close() {
    s.gameListener.Close()
    s.listener.Close()
}

func (s *Server)NewServer(tcpaddr string, tcpport int, udpaddr string, udpport int) error {
    // TCP listener
    addrTCP := &net.TCPAddr {
        Port: tcpport,
        IP: net.ParseIP(tcpaddr),
    }
    listener, err := net.ListenTCP("tcp", addrTCP)
    if err != nil {
        fmt.Printf("Error can't create s: %v", err)
        return err
    }
    s.listener = listener

    // UDP sock
    addrUDP := &net.UDPAddr{
        Port: udpport,
        IP:   net.ParseIP(udpaddr),
    }
    conn, err := net.ListenUDP("udp", addrUDP)
    if err != nil {
        fmt.Println("Error in creating s:", err)
        return err
    }

    // variables
    s.users = make(map[uint16]*User)
    s.gameListener = conn
    s.idCounter = 0
    s.serverOn = true

    return nil
}

func (s* Server)BroadcastGame() {
    // preallocate buffer and error
    data := make([]byte, 1024)
    // var err error = nil
    entity_data_prealloc := make([]*SerialisationEntityStruct, len(s.users))
    // for indexing enentity_data_prealloc
    i := 0

    ulen := 0 
    previusUlen := ulen

    for {
        if !s.serverOn {
            break
        }

        {
            // fmt.Println("Locking user mutex in BroadcastGame")
            s.userMutex.Lock()
            ulen = len(s.users)
            if ulen != previusUlen {
                fmt.Printf("Ulen changed: prev: %v, now%v\n", previusUlen, ulen)
                previusUlen = ulen
            }
            if ulen <= 0 {
                s.userMutex.Unlock();
                // fmt.Println("Unlocking user mutex in BroadcastGame")
                continue;
            }

            if len(entity_data_prealloc) < ulen {
                entity_data_prealloc = make([]*SerialisationEntityStruct, ulen)
                for i := 0; i< ulen; i++ {
                    entity_data_prealloc[i] = &SerialisationEntityStruct{}
                }
                fmt.Printf("reallocated entity_data_prealloc for size %v\n", ulen)
            }

            // reset entity_data_prealloc index --- ye... not this
            // how many updates
            // Serialise entity
            i = 0
            // for uInServerID, u := range s.users 
            for uInServerID, u := range s.users {
                u.dataMutex.Lock()
                if u.Entity.CurrentState != u.Entity.LastState {
                    s := NewSerialisationEntityStruct(
                        uInServerID,
                        u.Entity.CurrentState.Pos.x,
                        u.Entity.CurrentState.Pos.y,
                        u.Entity.CurrentState.State,
                        u.Entity.CurrentState.Direction,
                        )
                    entity_data_prealloc[i] = s
                    i++
                }
                u.dataMutex.Unlock()
            }
            s.userMutex.Unlock()
            if i <= 0 {
                // fmt.Printf("Nothing changed: %v\n", i)
                continue
            }
            fmt.Printf("Sending over %v entities\n", i)


            // Serialise message
            data = SerialiseEntities(entity_data_prealloc[:i])

            datal := len(data)
            if datal >= 1024 {
                fmt.Println("WARNING - data is over 1024 bytes. to handle. length:", datal)
                continue
            } else if datal <= 0 {
                fmt.Println("WARNING - data is 0 bytes. to handle. length:", datal)
                continue
            }

            s.userMutex.Lock()
            for _, u := range s.users {
                if u.UserOn {
                    _, err := s.gameListener.WriteToUDP(data, u.GameAddr)
                    // fmt.Println("sending data to:", u.inServerID, ":",u.addr)
                    if err != nil {
                        fmt.Println("Error in sending data to user game conn:", err)
                    }
                } else {
                    // delete user if user isn't on anymore
                    delete(s.users, u.InServerID)
                    fmt.Printf("Deleted user: %v:%v\n", u.InServerID, u.ID)
                    fmt.Println("Remaining users:")
                    for _,u := range s.users{
                        fmt.Println("\t",u)
                    }
                }
            }
            s.userMutex.Unlock()
        }
        // unlock s
    }

}

func (s *Server) HandleConns() {
    // accept user requests
    for {
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

        // handle request
        go s.HandleUserRequest(tcpConn)
    }
}
type userCommunicationStruct struct {
    Type        string `json:"type"`
    Message     interface{} `json:"message"`
}

// respond to user with json if error
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
// Add receiving a complete message rather than assuming data will be lwss than 1024 bytes
func (s *Server)HandleUserRequest(conn *net.TCPConn) {
    // make buffer
    buffer := make([]byte, 1024)

    // read request into buffer. if it fails, respond with error
    n, err := conn.Read(buffer)
    if err != nil {
        fmt.Println("HandleUserRequest Failed to read from user:", err)
        respondWithError(conn, err)
        return
    }

    // Get User Request
    msg, _, _, err := decodeMessage(buffer[:n])
    fmt.Println(msg)
    if err != nil {
        fmt.Println("Error in receiving user request:", err)
        respondWithError(conn, err)
        return
    }
    // fmt.Println(m, e, err)
    userJson := userCommunicationStruct{}

    err = json.Unmarshal([]byte(msg), &userJson)
    if err != nil {
        fmt.Println("Failed to Unmarshal Json: ", err)
        respondWithError(conn, err)
        return
    }

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

    fmt.Println("S mutex try locked")
    s.userMutex.Lock()
    fmt.Println("S mutex locked")
    // Create User
    if s.idCounter >= 100 || s.idCounter <= 0 {
        s.idCounter = 1
    }
    u := NewUser(int(id), uint16(s.idCounter), nil, conn)
    s.users[u.InServerID] = u
    fmt.Printf("User %v joined.\n", u.ID)
    
    // Respond with in s id
    // update to a more "full" response
    resp := struct{
        ID      int `json:"in_server_id"`
    }{ s.idCounter }

    s.idCounter++
    fmt.Println("S mux unlocked")
    s.userMutex.Unlock()

    respJsonBytes, err := json.Marshal(resp)
    b, err := encodeMessage(string(respJsonBytes))
    if err != nil {
        fmt.Println("Error in encoding message:",err)
        respondWithError(conn, err)
        return
    }

    conn.Write(b)
    go u.HandleGameData()
    go u.HandleEventMessages()
}

func (s *Server)GameListenerUDP() {
    buffLen := 1024
    buffer := make([]byte, buffLen)
    for {
        // Read the initial part of the message
        s.gameMutex.Lock()
        n, remoteAddr, err := s.gameListener.ReadFromUDP(buffer)
        s.gameMutex.Unlock()
        if err != nil {
            fmt.Println("Error in game listener(UDP):", err)
            continue
        }
        id, msg, err := decodeUDPMessage(buffer[:n])
        if err != nil {
            fmt.Println("In receiving data from user:", err)
            continue
        }
        // remoteAddrStr := remoteAddr.String()
        s.userMutex.Lock()
        u, exists := s.users[id]
        if !exists {
            fmt.Printf("Unauthorised user %v: %v.\n", id, remoteAddr.String())
            fmt.Print("In s ids\n\t")
            for _, u := range s.users {
                fmt.Print(",", u.InServerID)
            }
            fmt.Println()
            continue
        }
        if u.GameAddr == nil {
            u.GameAddr = remoteAddr
        }
        select {
        case u.Channel <- msg:
        default:
            fmt.Printf("User %d channel is full, dropping message\n", u.ID)
        }
        s.userMutex.Unlock()
    }
}
