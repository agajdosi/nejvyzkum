import general
import secrets, random
import tornado.websocket

class Index(general.GeneralHandler):
    def get(self):
        self.render("korona/index.html")
    def post(self):
        self.redirect("/korona/hra/" + secrets.token_hex(16))

class Hra(general.GeneralHandler):
    def get(self, token):
        self.render("korona/hra.html", token=token)

class WebSocket(tornado.websocket.WebSocketHandler):
    games = {}
    #games = {"ajftoken": {
    #    "clients": [object,object,object],
    #    "suspsects" : [id,id,id,id,id],
    #    "disabled": [id,id],
    #    "criminal": [id]
    #}

    def open(self, token):
        self.token = token
        if self.games.get(token) == None:
            self.games[token] = {}
            self.games[token]["suspects"] = generateSuspects()
            self.games[token]["criminal"] = self.games[token]["suspects"][random.randint(0,15)]
            self.games[token]["disabled"] = []
            self.games[token]["clients"] = [self]
        else:
            self.games[token]["clients"].append(self)
        
        print(self.games)

    def on_message(self, message):
        pass

    def on_close(self):
        self.games[self.token]["clients"].remove(self)
        if self.games[self.token]["clients"] == []:
            del self.games[self.token]

        print(self.games)

def generateSuspects():
    suspects = range(1,17)
    return suspects
