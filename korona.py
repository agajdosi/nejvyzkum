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
    #       "suspsects" : [id,id,id,id,id],
    #       "disabled": [id,id],
    #       "criminal": [id],
    #       "status": "started",
    #       "detective": cookie,
    #       "witness": cookie,
    #    }
    #}

    def open(self, token):
        self.token = token
        self.gameExists()
        if self.checkRole() == False:
            return
        if self.checkClient() == False:
            return

        print(self.games)
        updateAll(self.games[self.token])

    def on_message(self, message):
        pass

    def on_close(self):
        if self in self.games[self.token]["clients"]:
            self.games[self.token]["clients"].remove(self)
            self.games[self.token]["data"]["status"] = "paused"
            print("client left")
            print(self.games[self.token])
            updateAll(self.games[self.token])
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
        print("random")

    def gameExists(self):
        if self.games.get(self.token) != None:
            print("game exists")
            return
        self.games[self.token] = {"data": {} }
        self.games[self.token]["data"]["suspects"] = generateSuspects()
        self.games[self.token]["data"]["criminal"] = self.games[self.token]["data"]["suspects"][random.randint(0,15)]
        self.games[self.token]["data"]["disabled"] = []
        self.games[self.token]["data"]["detective"] = None
        self.games[self.token]["data"]["witness"] = None
        self.games[self.token]["data"]["status"] = "created"
        self.games[self.token]["clients"] = []
        print("game created")

    def checkClient(self):
        clients = len(self.games[self.token]["clients"]) 
        if clients >= 2:
            self.write_message("game is full")
            return False

        if clients == 1:
            self.games[self.token]["data"]["status"] = "running"
 
        self.games[self.token]["clients"].append(self)
        return True

def updateAll(game):
    json = tornado.escape.json_encode(game["data"])
    for client in game["clients"]:
        client.write_message(json)

def generateSuspects():
    suspects = list(range(1,17))
    return suspects
