token = null
ws = null

function openWS(token){
    token = token
    url = "ws://" + window.location.hostname + ":" + window.location.port + "/korona/ws/" + token
    ws = new WebSocket(url);

    ws.onmessage = function (evt) {
        if (evt.data == "game is full") {
            alert("Sorry this room is full");
            window.location = "../";
        };
        if (evt.data == "roles are taken") {
            alert("Sorry all roles were taken");
            window.location = "../";
        };
        if (evt.data == "already connected") {
            alert("Sorry you are already connected");
            window.location = "../";
        };
    };
}



