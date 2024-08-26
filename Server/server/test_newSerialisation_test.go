package server

import (
	"testing"
)

func TestSerialise(t *testing.T) {
	entity := SerialisationEntityStruct{
		InServerID: 123,
		X:          Change[int32]{Changed: true, Value: 100},
		Y:          Change[int32]{Changed: true, Value: 200},
		State:      Change[uint8]{Changed: true, Value: 1},
		Direction:  Change[uint16]{Changed: true, Value: 2},
	}

	serializedData, err := Serialise(&entity)
	if err != nil {
		t.Fatalf("Serialise failed: %v", err)
	}

	// Check if serialized data is not empty
	if len(serializedData) == 0 {
		t.Fatalf("Serialized data is empty")
	}

	// Deserialize and check if it matches the original entity
	deserializedEntity, _, err := Deserialise(serializedData, 0)
	if err != nil {
		t.Fatalf("Deserialise failed: %v", err)
	}

	// Compare fields
	if entity.InServerID != deserializedEntity.InServerID {
		t.Errorf("InServerID mismatch: expected %d, got %d", entity.InServerID, deserializedEntity.InServerID)
	}
	if entity.X.Changed != deserializedEntity.X.Changed || entity.X.Value != deserializedEntity.X.Value {
		t.Errorf("X mismatch: expected %d, got %d", entity.X.Value, deserializedEntity.X.Value)
	}
	if entity.Y.Changed != deserializedEntity.Y.Changed || entity.Y.Value != deserializedEntity.Y.Value {
		t.Errorf("Y mismatch: expected %d, got %d", entity.Y.Value, deserializedEntity.Y.Value)
	}
	if entity.State.Changed != deserializedEntity.State.Changed || entity.State.Value != deserializedEntity.State.Value {
		t.Errorf("State mismatch: expected %d, got %d", entity.State.Value, deserializedEntity.State.Value)
	}
	if entity.Direction.Changed != deserializedEntity.Direction.Changed || entity.Direction.Value != deserializedEntity.Direction.Value {
		t.Errorf("Direction mismatch: expected %d, got %d", entity.Direction.Value, deserializedEntity.Direction.Value)
	}
}

func TestSerialiseMany(t *testing.T) {
	entities := []*SerialisationEntityStruct{
		{
			InServerID: 123,
			X:          Change[int32]{Changed: true, Value: 100},
			Y:          Change[int32]{Changed: true, Value: 200},
			State:      Change[uint8]{Changed: true, Value: 1},
			Direction:  Change[uint16]{Changed: true, Value: 2},
		},
		{
			InServerID: 456,
			X:          Change[int32]{Changed: true, Value: 300},
			Y:          Change[int32]{Changed: true, Value: 400},
			State:      Change[uint8]{Changed: true, Value: 3},
			Direction:  Change[uint16]{Changed: true, Value: 4},
		},
	}

	serializedData, err := SerialiseMany(entities)
	if err != nil {
		t.Fatalf("SerialiseMany failed: %v", err)
	}

	// Check if serialized data is not empty
	if len(serializedData) == 0 {
		t.Fatalf("Serialized data is empty")
	}

	// Deserialize and check if they match the original entities
	deserializedEntities, _, err := DeserialiseMany(serializedData, 0)
	if err != nil {
		t.Fatalf("DeserialiseMany failed: %v", err)
	}

	// Compare each entity
	if len(deserializedEntities) != len(entities) {
		t.Fatalf("Number of deserialized entities does not match original")
	}

	for i, entity := range entities {
		deserializedEntity := deserializedEntities[i]
		if entity.InServerID != deserializedEntity.InServerID {
			t.Errorf("Entity %d: InServerID mismatch: expected %d, got %d", i, entity.InServerID, deserializedEntity.InServerID)
		}
		if entity.X.Changed != deserializedEntity.X.Changed || entity.X.Value != deserializedEntity.X.Value {
			t.Errorf("Entity %d: X mismatch: expected %d, got %d", i, entity.X.Value, deserializedEntity.X.Value)
		}
		if entity.Y.Changed != deserializedEntity.Y.Changed || entity.Y.Value != deserializedEntity.Y.Value {
			t.Errorf("Entity %d: Y mismatch: expected %d, got %d", i, entity.Y.Value, deserializedEntity.Y.Value)
		}
		if entity.State.Changed != deserializedEntity.State.Changed || entity.State.Value != deserializedEntity.State.Value {
			t.Errorf("Entity %d: State mismatch: expected %d, got %d", i, entity.State.Value, deserializedEntity.State.Value)
		}
		if entity.Direction.Changed != deserializedEntity.Direction.Changed || entity.Direction.Value != deserializedEntity.Direction.Value {
			t.Errorf("Entity %d: Direction mismatch: expected %d, got %d", i, entity.Direction.Value, deserializedEntity.Direction.Value)
		}
	}
}

