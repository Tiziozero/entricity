console.log("Works!!!");
socket = new WebSocket("ws://192.168.0.5:9999/ws")

var mainArea = "users"

socket.onopen = function(event) {
    console.log("WebSocket connection opened:", event);
    socket.send("Hello Server!");  // Example of sending data to the server
};


// Event handler when a message is received from the server
socket.onmessage = (event) => {
    console.log("Message received from server:", event.data);
    messages = JSON.parse(event.data);
    if (mainArea === "users") {
        for (let i = 0; i < messages.length; i++) {
            const pod = messages[i];
            const element = document.getElementById(pod.userId);
            if (element === null) {
                
            }
        }
    }
    // Handle the received message (e.g., display it in the UI)
};

const NewUserCapsule = (name, x, y, state) => {
}
