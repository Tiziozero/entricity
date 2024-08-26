package server

import (
	"context"
	"fmt"
	"net/http"
	"github.com/gorilla/websocket"
	"github.com/Tiziozero/entricity/Server/DashBoard"
)

// Upgrade the HTTP connection to a WebSocket connection
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true // Allow all origins, adjust as needed
    },
}

func SerialiseServerData(s *Server) interface{} {
    // s.userMutex.Lock()
    c := make(map[uint16]*User, len(s.users))
    for key, value := range s.users {
        c[key] = value
    }
    // s.userMutex.Unlock()
    return c
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
        component := src.DashBoard()
        component.Render(context.Background(), w)
    }
}

