package store

import (
    "fmt"
    "math/rand"
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
    Pfp             string  `json:"pfp"`
}


type Store struct {
    Users       []UserData
}


func NewStore() Store {
    store_ := Store{
        Users: make([]UserData, 0),
    }

    return store_
}
type SendUserData struct {
    ID int          `json:"id"`
    Name string     `json:"name"`
    Email string    `json:"email"`
    Pfp string      `json:"pfp"`
}
func (s *Store)GetUserData(userID int) (SendUserData, error) {
    for _, u := range s.Users {
        if u.ID == userID {
            u_ := SendUserData{
                u.ID, u.Name, u.Email, u.Pfp,
            }
            return u_, nil
        }
    }
    return SendUserData{}, ErrorUserNotFound
}

func (s *Store)LogInUser(identification, password string) error {
    for _,u := range s.Users {
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
    for _, u := range s.Users {
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
    s.Users = append(s.Users, u)
    return u, nil
}
func UserData2SendUserData(ud []UserData) []SendUserData {
    return src.Map(ud, func(u UserData) SendUserData {
        return SendUserData {
            ID: u.ID,
            Name: u.Name,
            Email: u.Email,
            Pfp: u.Pfp,
        }
    })
}
