package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"sync"
    "strconv"
    "math/rand"

	"github.com/Tiziozero/entricity/Server/store"
	"github.com/Tiziozero/entricity/Server/src"
	"github.com/gorilla/mux"
	// "github.com/gorilla/websocket"
)


type Server struct {
    listener            net.Listener
    gameListener        *net.UDPConn
    users               map[uint16]*User
    entities            map[uint16]*Entity
    listenerMutex       sync.Mutex
    gameMutex           sync.Mutex
    userMutex           sync.Mutex
    idCounter           int
    serverOn            bool
    store               *store.Store
    httpListener        *mux.Router
    dashboardWSConns    []*WSManagerUser

}
type userCommunicationStruct struct {
    Type                string `json:"type"`
    Message             interface{} `json:"message"`
}

func (s *Server)Close() {
    s.gameListener.Close()
    s.listener.Close()
}

func (s *Server)NewServer(tcpaddr string, tcpport int, udpaddr string, udpport int, httpPort int) error {
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
    
    store_ := store.NewStore()

    // variables
    s.users = make(map[uint16]*User)
    s.gameListener = conn
    s.idCounter = 0
    s.serverOn = true
    s.store = &store_
    for i := 0; i < 1000 - 1; i++ {
        user := store.UserData{
            ID:       i, // You can use a random ID if needed
            Name:     "User" + strconv.Itoa(rand.Intn(10000)),
            Email:    "user" + strconv.Itoa(i) + "@example.com",
            Password: src.GenerateRandomString(8),
            AccessToken: src.GenerateNewAccessToken(),
            Pfp: "https://i1.wp.com/katzenworld.co.uk/wp-content/uploads/2019/06/funny-cat.jpeg?fit=1920%2C1920&ssl=1",
        }
        // Append the user to the store
        store_.Users = append(store_.Users, user)
    }
    u := store.UserData{
        ID: 6969,
        Name: "Pasta",
        Email: "pasta@yahoo1.olg",
        Password: "PastaAt1",
        AccessToken: "ZrMRX3Y360tEfqFfDCcvmAcnKUdfSRlPWEOB0FD0nzfUnb4Dii9XNL29R8qiC9pCVSslHk85AdkgqX1JNa5V0JvvR6z7CefF4IpVxahKrIF36UQboYFO0ACvnj87CjCgShnIcpnUcqLrNcnGVOoK0tJdZhOZPX7WqgErL52ZxCyYahQdnyoFaHZyAgdhNwRPBPjIRBhP2kgEYTJaUCETuc5TpmnkGkJjYGvYo80K5cLXyVMjI6pkXq1FDdI2uhTR",
        Pfp: "https://i1.wp.com/katzenworld.co.uk/wp-content/uploads/2019/06/funny-cat.jpeg?fit=1920%2C1920&ssl=1",
    }
    fmt.Println("Created Users.")
    store_.Users = append(store_.Users, u)

    mux := mux.NewRouter()
    s.httpListener = mux

    ImagesFilePath := "./static/images"
    fs := http.FileServer(http.Dir("./static"))
    mux.PathPrefix("/static/").Handler(http.StripPrefix("/static/", fs))

    fsImgs := http.FileServer(http.Dir(ImagesFilePath))
	mux.PathPrefix("/resize/").Handler(http.StripPrefix("/resize/", src.ResizeImagesWithPath(nil, nil, ImagesFilePath)))
	mux.PathPrefix("/imgs/").Handler(http.StripPrefix("/imgs/", fsImgs))

    mux.HandleFunc("/users/get/{userid}", HTMXUserDataRender(s))
    mux.HandleFunc("/htmx-api/user-data", HTMXUserDataRender(s))

    mux.Handle("/admin",AdminDashboardHandler(s))
    mux.Handle("/ws",WSManager(s))

    go http.ListenAndServe(fmt.Sprintf("%s:%v",tcpaddr,httpPort), mux)   
    fmt.Printf("Started HTTP Server at: %s:%v\n", tcpaddr, httpPort)
    go s.BroadcastGame()
    fmt.Printf("Broadcast game at: %s:%v\n", udpaddr, udpport)
    go s.GameListenerUDP()
    fmt.Printf("Listening game at: %s:%v\n", udpaddr, udpport)

    fmt.Printf("Listening for connections at: %s:%v\n", tcpaddr, tcpport)
    s.HandleConns()
    return nil
}

func (s* Server)BroadcastGame() {
    // preallocate buffer and error
    data := make([]byte, 1024)
    var err error = nil
    entity_data_prealloc := make([]*SerialisationEntityStruct, len(s.users))
    // for indexing enentity_data_prealloc
    i := 0

    ulen := 0 
    previusUlen := ulen

    for {
        if !s.serverOn {
            break
        }

        // fmt.Println("User Mutex Locked in broadcast Game")
        s.userMutex.Lock()
        ulen = len(s.users)
        s.userMutex.Unlock()
        if ulen != previusUlen {
            //DEBUG
            fmt.Printf("Users length changed: prev: %v, now%v\n", previusUlen, ulen)
            previusUlen = ulen
        }
        if ulen <= 0 {
            continue;
        }

        if len(entity_data_prealloc) < ulen {
            entity_data_prealloc = make([]*SerialisationEntityStruct, ulen)
            for i := 0; i< ulen; i++ {
                entity_data_prealloc[i] = &SerialisationEntityStruct{}
            }
            //DEBUG
            fmt.Printf("reallocated entity_data_prealloc for size %v\n", ulen)
        }

        i = 0
        s.userMutex.Lock()
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
        // s.userMutex.Unlock();fmt.Println("Unloked User Mutex")
        if i <= 0 {
            // s.userMutex.Unlock();fmt.Println("Unloked User Mutex")
            continue
        }
        /*
        for _, e := range entity_data_prealloc {
            fmt.Print(e)
            fmt.Print("|")
        }
        fmt.Print("\n")
        */

        // fmt.Printf("Sending over %v entities\n", i)

        data, err = SerialiseMany(entity_data_prealloc[:i])
        if err != nil {
            fmt.Println("Error in serialising entities in broadcast game:", err)
        }

        datal := len(data)
        if datal >= 1024 {
            fmt.Println("WARNING - data is 1024 or more bytes. to handle. length:", datal)
            // s.userMutex.Unlock();fmt.Println("Unloked User Mutex")
            continue
        } else if datal <= 0 {
            fmt.Println("WARNING - data is 0 or less bytes. to handle. length:", datal)
            // s.userMutex.Unlock();fmt.Println("Unloked User Mutex")
            continue
        }
        // for now. to check if whole packet is received rather than just part of it
        bytesSerialisedEntitiesLength := packUint32(uint32(i))
        if len(bytesSerialisedEntitiesLength) <= 0 {
            fmt.Println("Failed to serialise packed entities length")
            continue
        }
        var sendData bytes.Buffer
        sendData.Write(bytesSerialisedEntitiesLength)
        sendData.Write(data)

        inactiveUsers := make([]uint16, 0)
        // fmt.Println("UserMutex Locked in sending data broadcast game")
        // s.userMutex.Lock()
        s.userMutex.Lock()
        for userInServerID, u := range s.users {
            if u.UserOn {
                if u.GameAddr == nil {
                    continue
                }
                // for now use sendData for debug of weather whole packet or just part of it gets received
                // _, err := s.gameListener.WriteToUDP(data, u.GameAddr)
                _, err := s.gameListener.WriteToUDP(sendData.Bytes(), u.GameAddr)
                if err != nil {
                    fmt.Println("Error in sending data to user game conn:", err)
                    // u.Close()
                }
            } else {
                inactiveUsers = append(inactiveUsers, userInServerID)
            }

        }
        d := SerialiseServerData(s)
        /*
        if len(s.dashboardWSConns) > 0 {
            fmt.Println(len(s.dashboardWSConns))
        }
        */
        for j, u := range s.dashboardWSConns {
            if u.on {
                // attention when using SerialiseServerData. It Doesn't use mutex
                // fmt.Println("Sending to j:", d)
                if err := u.c.WriteJSON(d); err != nil {
                    fmt.Println(err)
                    u.on = false
                }
            } else {
                s.dashboardWSConns = append(s.dashboardWSConns[:j], s.dashboardWSConns[j+1:]...)
            }
        }
        s.userMutex.Unlock()
        // s.userMutex.Unlock();fmt.Println("Unloked User Mutex")
        for _, userInServerID := range inactiveUsers {
            fmt.Println("Kill User:", userInServerID)
            s.RemoveUser(userInServerID)
        }
    }
}

func (s *Server)BroadcastGameToWSConns() {
    for s.serverOn {
        // yyeeeeee... idfk
    }
}

type userDisconnect struct {
    Type    string `json:"type"`
    ID      uint16 `json:"user_in_server_id"`
}
func (s *Server)RemoveUser(userInServerID uint16) {
    // fmt.Println("Locking user mutedx for removing user")
    s.userMutex.Lock()

    delete(s.users, userInServerID)

    //DEBUG
    fmt.Printf("Deleted user: %v\n", userInServerID)
    message:=userDisconnect{"user_disconnected", userInServerID}
    m := userCommunicationStruct{
        Type: "event",
        Message: message,
    }
    js, err := json.Marshal(&m)
    if err != nil {
        fmt.Println("Error in marshaling  userCommunicationStruct struct:", err)
        s.userMutex.Unlock()
        return
    }

    s.userMutex.Unlock()
    s.BroadcastEventMessage(js)
}

func (s *Server) HandleConns() {
    for {
        fmt.Println("Listening for connections")
        conn, err := s.listener.Accept()
        if err != nil {
            fmt.Println("Error accepting connection:", err)
            continue
        }
        //DEBUG
        // fmt.Println("Request from user:", conn)

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

// respond to user with json if error
func respondWithError(conn *net.TCPConn, err error) {
    r := userCommunicationStruct{"error", err.Error()}
    respJsonBytes, err := json.Marshal(r)
    b, err := src.EncodeMessage(string(respJsonBytes))
    if err != nil {
        fmt.Printf("Failed to write to user: %v", err)
        return
    }
    //DEBUG
    fmt.Println("Responding (with error) with:", string(b))
    conn.Write(b)

}

func (s *Server)HandleUserRequest(conn *net.TCPConn) {
    /* Request should look loke this:
    session-token should be a secret encrypted token uinque to each player
    based on player id an the specific server
    {
        "type": "connect",
        "message": {
            "id": id,
            "accesstoken": accesstoken,
            other info...
        }
    }
    */
    buffer := make([]byte, 1024)

    n, err := conn.Read(buffer)
    if err != nil {
        fmt.Println("HandleUserRequest Failed to read from user:", err)
        respondWithError(conn, err)
        return
    }

    l, err  := src.DecodeLengthFromBytes(buffer)
    if err != nil {
        fmt.Println("Error in receiving user request:", err)
        respondWithError(conn, err)
        return
    }
    if n < l+4 {
        fmt.Println("Incomplete message received")
        respondWithError(conn, fmt.Errorf("incomplete message received"))
        return

    }
    msg := buffer[4:4+l]
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
        fmt.Println("ID is not a valid float64/missing")
        respondWithError(conn, fmt.Errorf("Failed to construct from response json"))
        return
    }
    accesstoken, ok := messageMap["accesstoken"].(string) // JSON unmarshals numbers as float64
    if !ok {
        fmt.Println("accesstoken is not a valid string/missing")
        respondWithError(conn, fmt.Errorf("Failed to construct from response json"))
        return
    }
    udata, err := s.store.ValidateUserJoinRequest(int(id), accesstoken)
    if err != nil {
        respondWithError(conn, fmt.Errorf("invalid credentials"))
        return
    }
    fmt.Println(udata)

    

    s.userMutex.Lock()
    if s.idCounter >= 100 || s.idCounter <= 0 {
        s.idCounter = 1
    }
    u := NewUser(int(id), uint16(s.idCounter), nil, conn)
    s.users[u.InServerID] = u
    //DEBUG
    fmt.Printf("User %v joined.\n", u.ID)
    resp := struct{
        ID      int `json:"in_server_id"`
    }{ s.idCounter }
    s.idCounter++
    s.userMutex.Unlock()

    respJsonBytes, err := json.Marshal(resp)
    b, err := src.EncodeMessage(string(respJsonBytes))
    if err != nil {
        fmt.Println("Error in encoding message:",err)
        respondWithError(conn, err)
        return
    }

    conn.Write(b)
    go u.HandleGameData()
    go s.HandleUserEvents(u)
}

func (s *Server)HandleUserEvents(u *User) {
    buffer := make([]byte, 1024)
    for u.UserOn {
        buffer, err := src.DecodeMessage(u.EventConn, buffer)
        if err != nil {
            fmt.Println("User Event error:",err)
            u.Close()
            return
        }
        // handle event here
        fmt.Println(string(buffer))
    }
}
func (s *Server)BroadcastEventMessage(event []byte) {
    //DEBUG
    fmt.Println("Broadcasting:", string(event))
    msg, err := src.EncodeMessage(string(event))
    if err != nil {
        fmt.Println("Error in encoding message in broadcasting event msg:", err)
        return
    }
    s.userMutex.Lock()
    for userInServerID, u := range s.users {
        _, err := u.EventConn.Write(msg)
        if err != nil {
            s.userMutex.Unlock()
            s.RemoveUser(userInServerID)
            s.userMutex.Lock()
        }
    }
    s.userMutex.Unlock()
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
        id, msg, err := src.DecodeUDPMessage(buffer[:n])
        fmt.Println(id)
        if err != nil {
            fmt.Println("In receiving data from user:", err)
            continue
        }
        s.userMutex.Lock()
        u, exists := s.users[id]
        s.userMutex.Unlock()
        if !exists {
            fmt.Printf("Unauthorised user %v: %v.\n", id, remoteAddr.String())
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
    }
}
