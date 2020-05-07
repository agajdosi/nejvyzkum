import general
import secrets, random, copy
import tornado.websocket, tornado.escape

class Index(general.GeneralHandler):
    def get(self):
        self.render("korona/index.html")
    def post(self):
        self.redirect("/korona/hra/" + secrets.token_hex(16))

class Hra(general.GeneralHandler):
    def get(self, token):
        if self.get_cookie("nejvyzkum-player") == None:
            self.set_cookie("nejvyzkum-player", secrets.token_hex(32))
        
        self.render("korona/hra.html", token=token)

class WebSocket(tornado.websocket.WebSocketHandler):
    games = {}
    #z game asi idealne udelat proste objekt
    #games = {"ajftoken": {
    #    "clients": [object,object,object],
    #    "data": {
    #       "suspsects" : [{id:14,picture:url,name:name},...],
    #       "eliminated": [id,id],
    #       "criminal": [id],
    #       "status": "started",
    #       "finished": "no"
    #       "detective": cookie,
    #       "witness": cookie,
    #       "move": "detective",
    #       "question": "Fandi koronaviru?",
    #       "answer": "true"
    #    }
    #}

    def open(self, token):
        self.token = token
        self.gameExists()
        if self.checkRole() == False:
            return

        self.games[self.token]["clients"].append(self)
        self.updateAll()


    def on_message(self, message):
        if self.games[self.token]["data"]["finished"] == "lost":
            if "pls-restart-game" in message:
                self.restartGame()
            return

        if message == "true" or message == "false":
            print(message)
            self.games[self.token]["data"]["answer"] = message
            self.games[self.token]["data"]["turn"] = "detective"

        if "eliminated" in message:
            eliminated = int(message.split("=")[1])
            
            if eliminated == self.games[self.token]["data"]["criminal"]:
                self.games[self.token]["data"]["finished"] = "lost"
            else:
                self.games[self.token]["data"]["eliminated"].append(eliminated)
                self.games[self.token]["data"]["turn"] = "witness"

        self.updateAll()

    def on_close(self):
        if self in self.games[self.token]["clients"]:
            self.games[self.token]["clients"].remove(self)
            self.games[self.token]["data"]["status"] = "paused"
            print("client left")
            print(self.games[self.token])
            self.updateAll()
        else:
            print("non participating client left")

        if self.games[self.token]["clients"] == []:
            del self.games[self.token]
            print("the game has been deleted")

    def checkRole(self):
        cookie = self.get_cookie("nejvyzkum-player")
        detective = self.games[self.token]["data"]["detective"]
        witness = self.games[self.token]["data"]["witness"]
        
        if cookie == detective or cookie == witness:
            return True

        if detective == None and witness == None:
            if random.random() > 0.5:
                self.games[self.token]["data"]["detective"] = cookie
            else:
                self.games[self.token]["data"]["witness"] = cookie
            return True    

        if detective == None:
            self.games[self.token]["data"]["detective"] = cookie
            return True
        
        if witness == None:
            self.games[self.token]["data"]["witness"] = cookie
            return True
        
        if detective != None and witness != None:
            self.write_message("roles are taken")
            return False

    def gameExists(self):
        if self.games.get(self.token) != None:
            print("game exists")
            return

        self.games[self.token] = {"data": {} }
        self.games[self.token]["data"]["detective"] = None
        self.games[self.token]["data"]["witness"] = None
        self.games[self.token]["data"]["status"] = "created"
        self.games[self.token]["clients"] = []
        self.generateGameData()
        print("game created")

    def generateGameData(self):
        self.games[self.token]["data"]["suspects"] = generateSuspects()
        self.games[self.token]["data"]["question"] = generateQuestion()
        self.games[self.token]["data"]["criminal"] = random.randint(0,15)
        self.games[self.token]["data"]["eliminated"] = []
        self.games[self.token]["data"]["answer"] = None
        self.games[self.token]["data"]["finished"] = "no"
        self.games[self.token]["data"]["turn"] = "witness"

    def restartGame(self):
        self.generateGameData()
        self.games[self.token]["data"]["detective"], self.games[self.token]["data"]["witness"] = self.games[self.token]["data"]["witness"], self.games[self.token]["data"]["detective"]
        self.updateAll()

    def updateAll(self):
        print("game=", self.games[self.token])
        for client in self.games[self.token]["clients"]:
            if client.get_cookie("nejvyzkum-player") == self.games[self.token]["data"]["detective"]:
                game = copy.deepcopy(self.games[self.token]["data"])
                del game["criminal"]
            else:
                game = self.games[self.token]["data"]
            json = tornado.escape.json_encode(game)
            client.write_message(json)

### MOCKING FUNCTIONS
# needs to be written

def generateQuestion():
    return "Vnima pachatel/ka COVID-19 jako ocistu lidstva?"

def generateSuspects():
    suspects = []
    for x in range(0,16):
        suspect = {
            "id": x,
            "picture": "https://mgwdata.net/forbes/prod/uploads/2019/10/komarek_casual.jpg",
            "name": "Karl Komarxek"
        }
        suspects.append(suspect)

    return suspects
