console.log("Works!!!");
const socket = new WebSocket("ws://192.168.0.5:9999/ws")

var mainArea = "users"

socket.onopen = function(event) {
  console.log("WebSocket connection opened:", event);
  socket.send("Hello Server!");  // Example of sending data to the server
};

// TODO: implement binary protocol. This is too slow
// Event handler when a message is received from the server
socket.onmessage = (event) => {
  const m = JSON.parse(event.data);

  if (m.users) {
    const users = m.users;
    for (let key in users) {
      if (users.hasOwnProperty(key)) {
        console.log(`${key}:${users[key]}`);
        const uElement = document.getElementById(key);
        if (uElement === null) {
          continue;
        }
        console.log(`${key}-x`);
        const ux = document.getElementById(`${key}-x`);
        if (ux === null) {
          console.log("failed");
          continue;
        }
        ux.innerHTML = users[key].x;
        const uy = document.getElementById(`${key}-y`);
        console.log(`${key}-y`);
        if (uy === null) {
          console.log("failed");
          continue;
        }
        uy.innerHTML = users[key].y;
      }
    }
  } else {
    console.log("No Users");
    console.log(m);
  }
};

const NewUserCapsule = (name, x, y, state) => {
}
