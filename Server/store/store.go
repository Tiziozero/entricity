package store

import (
    "fmt"
    "math/rand"
    "strconv"
	"github.com/Tiziozero/entricity/Server/src"
)

const MESSAGE_HOME_NOTICE = -1
const MESSAGE_CHAT = 1

var ErrorFailedSession error = fmt.Errorf("Failed to retreive user session")
var ErrorInvalidCredentials error = fmt.Errorf("Invalid Credentials supplied")
var ErrorUserNotLoggedIn error = fmt.Errorf("User is not logged in") 
var ErrorUserNotFound error = fmt.Errorf("User not found") 

type UserData struct {
    ID              int     `json:"id"`
    Name            string  `json:"name"`
    Email           string  `json:"email"`
    Password        string  `json:"password"`
    AccessToken     string  `json:"accesstoken"`
}


type Store struct {
    users       []UserData
}


func NewStore() Store {
    store_ := Store{
        users: make([]UserData, 0),

    }
    for i := 1; i <= 10; i++ {
        // Create a random user
        user := UserData{
            ID:       i, // You can use a random ID if needed
            Name:     "User" + strconv.Itoa(rand.Intn(10000)),
            Email:    "user" + strconv.Itoa(i) + "@example.com",
            Password: src.GenerateRandomString(8),
            AccessToken: src.GenerateNewAccessToken(),
        }
        // Append the user to the store
        store_.users = append(store_.users, user)
        fmt.Println(user)
    }
    u := UserData{6969, "Pasta", "pasta@yahoo1.olg", "PastaAt1", "ZrMRX3Y360tEfqFfDCcvmAcnKUdfSRlPWEOB0FD0nzfUnb4Dii9XNL29R8qiC9pCVSslHk85AdkgqX1JNa5V0JvvR6z7CefF4IpVxahKrIF36UQboYFO0ACvnj87CjCgShnIcpnUcqLrNcnGVOoK0tJdZhOZPX7WqgErL52ZxCyYahQdnyoFaHZyAgdhNwRPBPjIRBhP2kgEYTJaUCETuc5TpmnkGkJjYGvYo80K5cLXyVMjI6pkXq1FDdI2uhTR"}
    fmt.Println(u)
    store_.users = append(store_.users, u)
    return store_
}

func (s *Store)LogInUser(identification, password string) error {
    for _,u := range s.users {
        if u.Name == identification || u.Email == identification {
            if u.Password == password {
                    // Handle Successful Login
                return nil
            } else {
                return ErrorInvalidCredentials
            }
        }
    }
    return ErrorInvalidCredentials
}
func (s *Store)LogOutUser() error {
    return nil
}

func (s *Store)ValidateUserJoinRequest(id int, accesstoken string) (UserData, error) {
    for _, u := range s.users {
        if u.ID == id && u.AccessToken == accesstoken {
            return u, nil
        }
    }
    return UserData{}, ErrorUserNotFound
}


func (s *Store)NewUser(name, email, password string) (UserData, error) {
    u := UserData{
        Name: name,
        Email: email,
        Password: password,
        ID: rand.Int(),
    }
    s.users = append(s.users, u)
    return u, nil
}
