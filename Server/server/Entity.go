package server

import "fmt"

type Entity struct {
    InServerID      uint16
    CurrentState    EntityState
    LastState       EntityState
}
type EntityState struct {
    Pos             Vector2
    State           uint8
    Direction       uint16
    Health          int
}

func (es EntityState) String() string {
    return fmt.Sprintf("Pos: (%5d, %5d), State: %d, Direction: %d, Health: %d", es.Pos.x, es.Pos.y, es.State, es.Direction, es.Health)
}
