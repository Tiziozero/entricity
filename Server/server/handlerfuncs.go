package server

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	dashboard "github.com/Tiziozero/entricity/Server/Dashboard"
	"github.com/Tiziozero/entricity/Server/store"
	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
)

// Upgrade the HTTP connection to a WebSocket connection
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true // Allow all origins, adjust as needed
    },
}

type UserWSSendData struct {
    X int32 `json:"x"`
    Y int32 `json:"y"`
}
func SerialiseServerData(s *Server) interface{} {
    // s.userMutex.Lock()
    d := make(map[string]interface{})
    c := make(map[uint16]UserWSSendData, len(s.users))
    for _, u := range s.users {
        c[u.InServerID] = UserWSSendData{
            X: u.Entity.CurrentState.Pos.x,
            Y: u.Entity.CurrentState.Pos.y,
        }
    }
    d["users"] = c
    // s.userMutex.Unlock()
    return d
}

type WSManagerUser struct {
    c *websocket.Conn
    on bool
}
func WSManager(s *Server) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        c, err := upgrader.Upgrade(w, r, nil)
        if err != nil {
            fmt.Println("Failed to upgrade to websocket Connection:", err)
            return
        }
        u := &WSManagerUser{c, true}
        fmt.Println("Websocket Connection established")
        s.dashboardWSConns = append(s.dashboardWSConns, u)
        fmt.Println("Added WSConn user:", s.dashboardWSConns)
        /*
        go func(u *WSManagerUser){
            for u.on{
                if err := u.c.WriteJSON(SerialiseServerData(s)); err != nil {
                    fmt.Println(err)
                    u.on = false
                    break
                }
            }
            fmt.Println("Exiting Websocket reader goroutine")
        }(u)
        */
        go func(u *WSManagerUser) {
            for u.on {
                msgType, msg, err := u.c.ReadMessage()
                if err != nil {
                    fmt.Println(err)
                    u.on = false
                    break
                }
                fmt.Println(msgType, msg, err)
            }
            fmt.Println("Exiting Websocket reader goroutine")
        }(u)
    }
}
func AdminDashboardHandler(s *Server) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        users := store.UserData2SendUserData(s.store.Users)
        component := dashboard.DashBoard(dashboard.DashBoardBody([]string{"Hello", "No"}, users))
        component.Render(context.Background(), w)
    }
}
func GetUserData(s *Server) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        // uid := r.PathValue("userid")
        vars := mux.Vars(r)
        uid := vars["userid"]
        intUID, err := strconv.Atoi(uid)
        if err != nil {
            fmt.Printf("Can't convert path value uid: %v to int: %v\n",uid, err )
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }
        fmt.Printf("Requested data for user data: %d\n", intUID)
        userData, err := s.store.GetUserData(intUID)
        if err != nil {
            fmt.Printf("Can't find user: %d: %v\n.", intUID, err)
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }
        jsData, err := json.Marshal(userData)
        if err != nil {
            fmt.Printf("Failed to marshal json for user data\n")
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        w.Header().Set("Content-Type", "application/json")
        w.Write(jsData)
    }
}

func HTMXUserDataRender(s *Server) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        vars := mux.Vars(r)
        uid := vars["userid"]
        intUID, err := strconv.Atoi(uid)
        if err != nil {
            fmt.Printf("Can't convert path value uid: %v to int: %v\n",uid, err )
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }
        fmt.Printf("Requested data for user data: %d\n", intUID)
        userData, err := s.store.GetUserData(intUID)
        if err != nil {
            fmt.Printf("Can't find user: %d: %v\n.", intUID, err)
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }
        if err := dashboard.UserDetailsContent(userData).Render(r.Context(), w);
            err != nil {
            fmt.Println("Couldn't Render component:", err)
            http.Error(w, fmt.Sprint("Couldn't Render component:", err), http.StatusInternalServerError)
            return
        }
    }
}

