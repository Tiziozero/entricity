package server

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
