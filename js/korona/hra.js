identity = getCookie("nejvyzkum-player")
token = null
ws = null
game = null

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
    console.log(game);

    if (identity == game["witness"]) {
        handleWitness(game);
    }
    if (identity == game["detective"]) {
        handleDetective(game);
    }

    for (i=0; i<game["eliminated"].length; i++) {
        e = parseInt(game["eliminated"][i])
        document.getElementById("eliminated"+e).style.display = "block";
    }

    if (game["answer"] == "true") {
        document.getElementById("answer").innerText = "ANO!"
    } else {
        document.getElementById("answer").innerText = "NE!"
    }

    document.getElementById("question").innerText = game["question"]
}

function handleWitness(game){
    document.getElementById("role").innerText = "You are a Witness!";
    document.getElementById("witnessUI").style.display = "block";
    criminal = parseInt(game["criminal"])
    document.getElementById(criminal).innerText = "PACHATEL/KA!";

    if (game["turn"] == "witness"){
        document.getElementById("yes").disabled = false;
        document.getElementById("no").disabled = false;
        document.getElementById("answer").style.display = "none";
        document.getElementById("onmove").innerText = "Jste na rade!"
    } else {
        document.getElementById("yes").disabled = true;
        document.getElementById("no").disabled = true;
        document.getElementById("answer").style.display = "block";
        document.getElementById("onmove").innerText = "Hraje policajt!"
    }

}

function handleDetective(game){
    document.getElementById("role").innerText = "You are a Detective!";
    document.getElementById("detectiveUI").style.display = "block";

    if (game["turn"] == "detective"){
        document.getElementById("send").disabled = false;
        document.getElementById("answer").style.display = "block";
        document.getElementById("onmove").innerText = "Jste na rade!"
    } else {
        document.getElementById("send").disabled = true;
        document.getElementById("answer").style.display = "none";
        document.getElementById("onmove").innerText = "Hraje svedek!"
    }
}

function witnessAnswer(answer) {
    ws.send(answer);
}

function suspectClick(id) {
    if (game["turn"] == "witness") {
        return
    }

    message = "eliminated=" + parseInt(id)
    ws.send(message)
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
