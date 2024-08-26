package server

type Item struct {}
type Cell struct {}

type Map struct {
    items       map[uint16]Item
    cells       []Cell
}

func NewMap() *Map {
    return &Map{
        items: make(map[uint16]Item),
        cells: make([]Cell, 0),
    }
}

func (m *Map)LoadFrom(path string) error {
    // todo
    return nil
}


