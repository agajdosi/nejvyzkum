identity = getCookie("nejvyzkum-player")
token = null
ws = null


function openWS(token){
    token = token
    url = "ws://" + window.location.hostname + ":" + window.location.port + "/korona/ws/" + token
    ws = new WebSocket(url);

    ws.onmessage = function (evt) {
        if (evt.data == "roles are taken") {
            alert("Sorry all roles were taken");
            window.location = "../";
            return
        };

        parseGameData(evt);

    };
}

function parseGameData(evt){
    game = JSON.parse(evt.data);
    console.log(game)
    
    if (identity == game["witness"]) {
        document.getElementById("role").innerText = "You are a Witness!"
    }
    if (identity == game["detective"]) {
        document.getElementById("role").innerText = "You are a Detective!"
    }
}





function endTurn() {
    console.log("it has been sent");
}

function getCookie(name) {
    var cookieArr = document.cookie.split(";");
    for(var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        if(name == cookiePair[0].trim()) {
            return cookiePair[1];
        }
    }
    return null;
}
