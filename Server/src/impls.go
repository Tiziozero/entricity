package src

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"image"
	"image/jpeg"
	"image/png"
	"math/rand"
	"net"
	"net/http"
	"os"
	"path/filepath"

	"github.com/nfnt/resize"
)

// const IP_ADDR = "127.0.0.1"
const IP_ADDR = "192.168.0.5"

func bytesToUint16(b []byte) uint16 {
    return binary.BigEndian.Uint16(b)
}
func intToBytes(n int) []byte {
    // Create a byte slice with a length of 4 (for int32) or 8 (for int64)
    byteArray := make([]byte, 4)
    binary.BigEndian.PutUint32(byteArray, uint32(n))
    return byteArray
}
func EncodeMessage(message string) ([]byte, error) {
    length := int32(len(message))
    buf := new(bytes.Buffer)

    // Write the length of the message (4 bytes)
    err := binary.Write(buf, binary.BigEndian, length)
    if err != nil {
        return nil, err
    }
    // fmt.Println(buf.Bytes()[:4])

    // Write the message itself
    buf.Write([]byte(message))
    // fmt.Println(buf.Bytes()[:4])

    return buf.Bytes(), nil
}
// decodeMessage decodes a length-prefixed message.

// Returns the message, a boolean indicating if more data is needed, the number of missing bytes, and an error if any.
func DecodeMessage(c *net.TCPConn, buffer []byte) ([]byte, error) {
    n, err := c.Read(buffer)
    var got int = n
    // int
    const lengthPrefixSize = 4

    if len(buffer) < lengthPrefixSize {
        // Not enough buffer to read the length prefix
        return nil, fmt.Errorf("Not enough data/data too short to decode")
    }

    buf := bytes.NewBuffer(buffer)

    // Read the length of the message (4 bytes)
    var length int32
    err = binary.Read(buf, binary.BigEndian, &length)
    if err != nil {
        return nil, err
    }
    //DEBUG
    fmt.Printf("Expected Lenght of buffer: %v\n", length)


    totalLength := int(length) + lengthPrefixSize // Message length plus the 4 bytes of the length field
    if len(buffer) < int(totalLength) {
        buffer = make([]byte, length)
    }

    for got < totalLength {
        // Not enough buffer to read the full message
        n, err := c.Read(buffer[n:])
        if err != nil || n == 0 {
            return nil, fmt.Errorf("User Disconnected")
        }
        got += n
    }
    fmt.Println(buffer[lengthPrefixSize:])
    return buffer[lengthPrefixSize:], nil
}
func DecodeLengthFromBytes(buffer []byte) (int, error) {
    buf := bytes.NewBuffer(buffer)
    var length int32
    err := binary.Read(buf, binary.BigEndian, &length)
    if err != nil {
        return -1, err
    }
    return int(length), nil
}
// DecodeMessage takes a slice of bytes and decodes it into a user ID and user data.
func DecodeUDPMessage(data []byte) (uint16, []byte, error) {
	if len(data) < 2 {
		return 0, nil, fmt.Errorf("data too short, must be at least 2 bytes")
	}
	
	// Read the first 2 bytes as a uint16 user ID
	userID := binary.BigEndian.Uint16(data[:2])
	
	// The rest of the data is the user data
	userData := data[2:]
    // fmt.Println(userID, userData, data)
	
	return userID, userData, nil
}

func GenerateRandomString(n int) string {
    letters := []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    s := make([]rune, n)
    for i := range s {
        s[i] = letters[rand.Intn(len(letters))]
    }
    return string(s)
}

func GenerateNewAccessToken() string {
    return GenerateRandomString(256)
} 

func GetFileNamesInDir(dir string) []string {
	var fileNames []string

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() { // Check if it's not a directory
			fileNames = append(fileNames, info.Name()) // Append the file name to the slice
		}
		return nil
	})

	if err != nil {
		return make([]string, 0)

	}

	return fileNames
}

func ResizeImagesWithPath(w http.ResponseWriter, r *http.Request, ImagePath string) http.HandlerFunc {
    fmt.Printf("Called ResizeImagesWithPath with filename: %s\n", ImagePath)
    /*
    files, err := os.ReadDir(ImagePath)
	if err != nil {
        fmt.Println("Failed to open filepath:", ImagePath, err)
	}

	// Iterate over the files and print their names
	for _, file := range files {
		if !file.IsDir() {
			fmt.Println(file.Name())
		}
	}
    */
    return func(w http.ResponseWriter, r *http.Request) {
        imagePath := filepath.Join(ImagePath, r.URL.Path)
        // fmt.Printf("Called ResizeImagesWithPath with filename: %s\n", imagePath)
        file, err := os.Open(imagePath)
        if err != nil {
            http.Error(w, "Image not found", http.StatusNotFound)
            return
        }
        defer file.Close()

        // Decode the image
        img, format, err := image.Decode(file)
        if err != nil {
            http.Error(w, "Failed to decode image", http.StatusInternalServerError)
            return
        }

        // Get the dimensions of the image
        bounds := img.Bounds()
        width := bounds.Dx()
        height := bounds.Dy()

        // Determine the new dimensions to maintain aspect ratio
        var newWidth, newHeight uint
        if width < height {
            newWidth = 100
            newHeight = uint((height * 100) / width)
        } else {
            newHeight = 100
            newWidth = uint((width * 100) / height)
        }

        // Resize the image
        resizedImg := resize.Resize(newWidth, newHeight, img, resize.Lanczos3)

        // Encode the resized image to the response writer
        switch format {
        case "jpeg":
            w.Header().Set("Content-Type", "image/jpeg")
            jpeg.Encode(w, resizedImg, nil)
        case "png":
            w.Header().Set("Content-Type", "image/png")
            png.Encode(w, resizedImg)
        default:
            http.Error(w, "Unsupported image format", http.StatusUnsupportedMediaType)
        }
    }
}
func Map[T any, U any](items []T, fn func(T) U) []U {
	result := make([]U, len(items))
	for i, item := range items {

		result[i] = fn(item)
	}
	return result
}
