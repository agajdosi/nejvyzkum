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
        handleWitness();
    }
    if (identity == game["detective"]) {
        handleDetective();
    }

    renderSuspects();
    renderQuestion();
    renderAnswer();
    renderGameOver();
    renderGameWon();
}

var fields = [
    ["mainsource", "zdroj financí"],
    ["sidesource", "vedlejší zdroj financí"],
    ["birthday", "narození"],
    ["residence", "bydliště"],
    ["birthplace", "místo narození"],
    ["education", "vzdělání"],
    ["maritalstatus", "rodinný stav"],
    ["children", "děti"],
    ["obsession", "posedlost"],
    ["car", "auto"],
    ["maincompany", "firma"],
    ["sidecompanies", "vedlejší firmy"],
    ["wealthorigin", "původ majetku"],
    ["wealth", "jmění"],
];

var fieldsEN = [
    ["mainsource-en", "financial source"]
    ["sidesource-en", "side fin. sources"],
    ["birthday", "birthday"],
    ["residence-en", "residence"],
    ["birthplace-en", "birthplace"],
    ["education-en", "education"],
    ["maritalstatus-en", "marital status"],
    ["children", "children"],
    ["obsession-en", "obsession"],
    ["car", "car"],
    ["maincompany-en", "main company"],
    ["sidecompanies-en", "side companies"],
    ["wealthorigin-en", "wealth origin"],
    ["wealth-en", "total wealth"],
];

function renderSuspects() {
    for(var i = 0; i < game["suspects"].length; i++) {
        document.getElementById(i).getElementsByClassName("portrait")[0].src = game["suspects"][i]["image"];
        document.getElementById(i).getElementsByClassName("criminal")[0].innerText = null;
        document.getElementById(i).style.backgroundColor = "unset";
        document.getElementById(i).getElementsByClassName("eliminated")[0].style.display = "none";

        document.getElementById(i).getElementsByClassName("name")[0].innerText = game["suspects"][i]["name"];

        a = game["hints"]
        key = fields[a][0]
        caption = fields[a][1]
        value = game["suspects"][i][key]

        if (value == null){
            value = "?"
        };

        document.getElementById(i).getElementsByClassName("infoKey")[0].innerText = caption;
        document.getElementById(i).getElementsByClassName("infoValue")[0].innerText = value;
    }

    for (var i = 0; i < game["eliminated"].length; i++) {
        e = parseInt(game["eliminated"][i])
        document.getElementById(e).getElementsByClassName("eliminated")[0].style.display = "block";
    }

    if ("criminal" in game) {
        document.getElementById(game["criminal"]).getElementsByClassName("criminal")[0].innerText = "PACHATEL/KA";
        document.getElementById(game["criminal"]).style.backgroundColor = "rgb(255, 80, 80)";
    }
}

function renderQuestion() {
    document.getElementById("question").innerText = game["question"]["cz"];
}

function renderAnswer() {
    if (game["turn"] == "witness"){
        document.getElementById("answer").innerText = "___"
        return
    }
    
    if (game["answer"] == "true") {
        document.getElementById("answer").innerText = "ANO!"
    } else {
        document.getElementById("answer").innerText = "NE!"
    }
}

function renderGameOver(){
    if (game["finished"] == "lost"){
        document.getElementById("game-lost").style.display = "block";
    } else {
        document.getElementById("game-lost").style.display = "none";
    }
}

function renderGameWon(){
    if (game["finished"] == "won"){
        document.getElementById("game-won").style.display = "block";
    } else {
        document.getElementById("game-won").style.display = "none";
    }
}

function handleWitness(){
    document.getElementById("role").innerText = "Jste svědek";
    document.getElementById("witnessUI").style.display = "block";
    //document.getElementById("detectiveUI").style.display = "none";

    if (game["turn"] == "witness"){
        document.getElementById("yes").disabled = false;
        document.getElementById("no").disabled = false;
        document.getElementById("onmove").innerText = "Odpovězte na otázku!"
    } else {
        document.getElementById("yes").disabled = true;
        document.getElementById("no").disabled = true;
        document.getElementById("onmove").innerText = "Vyšetřovatel propouští..."
    }

}

function handleDetective(){
    document.getElementById("role").innerText = "Jste vyšetřovatel";
    //document.getElementById("detectiveUI").style.display = "block";
    document.getElementById("witnessUI").style.display = "none";

    if (game["turn"] == "detective"){
        //document.getElementById("send").disabled = false;
        document.getElementById("onmove").innerText = "Pusťte podezřelého, který nevyhovuje!"
    } else {
        //document.getElementById("send").disabled = true;
        document.getElementById("onmove").innerText = "Svěděk odpovídá..."
    }
}

function witnessAnswer(answer) {
    ws.send(answer);
}

function suspectClick(id) {
    if (game["turn"] == "witness") {
        return
    }

    if (identity == game["witness"]) {
        return
    }

    message = "eliminated=" + parseInt(id)
    ws.send(message)
}

function restartGame(){
    ws.send("pls-restart-game")
    console.log("restart sent")
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

function openHelp() {
    document.getElementById("napovedaLayer").style.display = "block";
    document.getElementById("link").innerText = document.location;
}

function closeHelp() {
    document.getElementById("napovedaLayer").style.display = "none";
}
