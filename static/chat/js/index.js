// Conexión WebSocket
const socket = new WebSocket(`ws://${window.location.host}/ws/chat/${username}/`);


const divMessage = $("#chat-messages");
const notificationsDiv = $("#notifications");
const usersDiv = $("#users");

// Mensajes entrantes
socket.onmessage = (e) => {
    const data = JSON.parse(e.data);

    switch (data.type) {
        case "message":
            addMessage(data);
            break;

        case "notification":
            addNotification(data.message);
            break;

        case "users_list":                 
            updateUsersList(data.users);
            break;

        default:
            console.warn("Tipo de mensaje no reconocido:", data.type);
            break;
    }
};

// Agregar mensaje al chat
function addMessage(data) {
    const isUser = username === data.username;

    let rawTime = data.timestamp || "";
    rawTime = rawTime.replace(/Z+$/, "Z");

    let time;
    try {
        const dateObj = new Date(rawTime);
        time = isNaN(dateObj.getTime())
            ? "justo ahora"
            : dateObj.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });
    } catch {
        time = "justo ahora";
    }

    const bubble = `
        <div class="d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'} mb-2">
        ${!isUser ? `
          <div class="me-2">
            <div class="bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center" 
                style="width: 35px; height: 35px; font-size: 0.9rem; font-weight: 600;">
              ${data.username.charAt(0).toUpperCase()}
            </div>
          </div>` : ''}

          <div class="d-flex flex-column ${isUser ? 'align-items-end' : 'align-items-start'}">
            <div class="p-2 px-3 rounded-3 shadow-sm ${isUser ? 'bg-success text-white rounded-end-0' : 'bg-light text-dark rounded-start-0'}">
              ${!isUser ? `<div class="fw-semibold text-primary small mb-1">${data.username}</div>` : ''}
              <div>${data.message}</div>
              <div class="text-end small opacity-75 mt-1">${time}</div>
            </div>
          </div>
        </div>
    `;

    divMessage.append(bubble);
    divMessage.scrollTop(divMessage.prop("scrollHeight"));
}

// Notificaciones
function addNotification(msg) {
    const notif = $(`
        <div class="alert alert-info alert-dismissible fade show py-2 small text-center" role="alert">
            ${msg}
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
        </div>
    `);
    notificationsDiv.prepend(notif);
    setTimeout(() => notif.alert("close"), 4000);
}

// Actualizar lista de usuarios
function updateUsersList(users) {
    usersDiv.empty();

    users.forEach(user => {
        const isCurrent = user === username;

        usersDiv.append(`
            <li class="list-group-item d-flex align-items-center border-0 bg-transparent">
                <i class="fa-solid fa-circle ${isCurrent ? 'text-success' : 'text-secondary'} me-2" style="font-size: 8px;"></i>
                ${isCurrent ? `<strong>${user}</strong>` : user}
            </li>
        `);
    });
}

// Enviar mensajes
$("#chat-form").on("submit", (e) => {
    e.preventDefault();
    const messageInput = $("#message");
    const message = messageInput.val().trim();

    if (message) {
        socket.send(JSON.stringify({ message }));
        messageInput.val("").focus();
    }
});

// Boton salir
$("#salir").on("click", () => {
    socket.close(1000);
    addNotification("Te has desconectado del chat.");
});
