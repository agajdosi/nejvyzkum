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
    ["quote", "citát"],
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
    ["quote-en", "quote"],
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
        document.getElementById(i).getElementsByClassName("eliminated")[0].style.display = "none";

        document.getElementById(i).getElementsByClassName("name")[0].innerText = game["suspects"][i]["name"];

        a = game["hints"][0]
        key1 = fields[a][0]
        caption1 = fields[a][1]
        text1 = caption1 + ": " + game["suspects"][i][key1]
        document.getElementById(i).getElementsByClassName("info1")[0].innerText = text1;

        b = game["hints"][1]
        key2 = fields[b][0]
        caption2 = fields[b][1]
        text2 = caption2 + ": " + game["suspects"][i][key2]
        document.getElementById(i).getElementsByClassName("info2")[0].innerText = text2;

        c = game["hints"][2]
        key3 = fields[c][0]
        caption3 = fields[c][1]
        text3 = caption3 + ": " + game["suspects"][i][key3]
        document.getElementById(i).getElementsByClassName("info3")[0].innerText = text3;
    }

    for (var i = 0; i < game["eliminated"].length; i++) {
        e = parseInt(game["eliminated"][i])
        document.getElementById(e).getElementsByClassName("eliminated")[0].style.display = "block";
    }

    if ("criminal" in game) {
        document.getElementById(game["criminal"]).getElementsByClassName("criminal")[0].innerText = "PACHATEL/KA!";
    }
}

function renderQuestion() {
    document.getElementById("question").innerText = game["question"]["cz"];
}

function renderAnswer() {
    if (game["turn"] == "witness"){
        document.getElementById("answer").style.display = "none";
    } else {
        document.getElementById("answer").style.display = "block";
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
        document.getElementById("game-won").style.display = "won";
    }
}

function handleWitness(){
    document.getElementById("role").innerText = "You are a Witness!";
    document.getElementById("witnessUI").style.display = "block";
    //document.getElementById("detectiveUI").style.display = "none";

    if (game["turn"] == "witness"){
        document.getElementById("yes").disabled = false;
        document.getElementById("no").disabled = false;
        document.getElementById("onmove").innerText = "Jste na rade!"
    } else {
        document.getElementById("yes").disabled = true;
        document.getElementById("no").disabled = true;
        document.getElementById("onmove").innerText = "Hraje policajt!"
    }

}

function handleDetective(){
    document.getElementById("role").innerText = "You are a Detective!";
    //document.getElementById("detectiveUI").style.display = "block";
    document.getElementById("witnessUI").style.display = "none";

    if (game["turn"] == "detective"){
        //document.getElementById("send").disabled = false;
        document.getElementById("onmove").innerText = "Jste na rade!"
    } else {
        //document.getElementById("send").disabled = true;
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

    if (identity == game["witness"]) {
        return
    }

    message = "eliminated=" + parseInt(id)
    ws.send(message)
}

function restartGame(){
    ws.send("pls-restart-game")
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
