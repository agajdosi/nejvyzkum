import secrets, random, copy
import tornado.websocket, tornado.escape
import general, database

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
    #       "suspsects" : [{id:14,image:url,name:name},...],
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
            self.questionAnswered(message)

        if "eliminated" in message:
            self.suspectEliminated(message)

        self.updateAll()

    def on_close(self):
        if self in self.games[self.token]["clients"]:
            self.games[self.token]["clients"].remove(self)
            self.games[self.token]["data"]["status"] = "paused"
            self.updateAll()
        else:
            pass

        if self.games[self.token]["clients"] == []:
            del self.games[self.token]

    def questionAnswered(self, msg):
        self.games[self.token]["data"]["answer"] = msg
        self.games[self.token]["data"]["turn"] = "detective"

        # should be moved into a function
        answer = 0
        question = int(self.games[self.token]["data"]["question"]["id"])
        activeSuspects = len(self.games[self.token]["data"]["suspects"]) - len(self.games[self.token]["data"]["eliminated"])
        if self.games[self.token]["data"]["answer"] == "true":
            answer = 1.0
        elif self.games[self.token]["data"]["answer"] == "false":
            answer = -1.0
        else:
            answer = 0
        for i in range(len(self.games[self.token]["data"]["suspects"])):
            if i in self.games[self.token]["data"]["eliminated"]:
                pass
            elif i == int(self.games[self.token]["data"]["criminal"]):
                ID = self.games[self.token]["data"]["suspects"][i]["id"]
                database.InsertAnswer(question, answer, ID, None)
            else:
                ID = self.games[self.token]["data"]["suspects"][i]["id"]
                database.InsertAnswer(question, -answer/(activeSuspects-1), ID, None)
        ###


    def suspectEliminated(self, msg):
        eliminated = int(msg.split("=")[1])
        if eliminated in self.games[self.token]["data"]["eliminated"]:
            return
        if self.games[self.token]["data"]["finished"] != "no":
            return

        # should be moved into a function
        answer = 0
        question = int(self.games[self.token]["data"]["question"]["id"])
        activeSuspects = len(self.games[self.token]["data"]["suspects"]) - len(self.games[self.token]["data"]["eliminated"])
        if self.games[self.token]["data"]["answer"] == "true":
            answer = -1.0
        elif self.games[self.token]["data"]["answer"] == "false":
            answer = 1.0
        else:
            answer = 0
        for i in range(len(self.games[self.token]["data"]["suspects"])):
            if i in self.games[self.token]["data"]["eliminated"]:
                pass
            elif i == eliminated:
                ID = self.games[self.token]["data"]["suspects"][i]["id"]
                database.InsertAnswer(question, answer, ID, None)
            else:
                ID = self.games[self.token]["data"]["suspects"][i]["id"]
                database.InsertAnswer(question, -answer/(activeSuspects-1), ID, None)
        ###

        self.games[self.token]["data"]["eliminated"].append(eliminated)
        if eliminated == self.games[self.token]["data"]["criminal"]:
            self.games[self.token]["data"]["finished"] = "lost"
            return
        
        if len(self.games[self.token]["data"]["eliminated"]) == 15:
            self.games[self.token]["data"]["finished"] = "won"
            return
        
        self.games[self.token]["data"]["turn"] = "witness"
        self.games[self.token]["data"]["question"] = database.GetRandomQuestion("korona")

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
            return

        self.games[self.token] = {"data": {} }
        self.games[self.token]["data"]["detective"] = None
        self.games[self.token]["data"]["witness"] = None
        self.games[self.token]["data"]["status"] = "created"
        self.games[self.token]["clients"] = []
        self.generateGameData()

    def generateGameData(self):
        self.games[self.token]["data"]["suspects"] = database.GetRandomPersons(16)
        self.games[self.token]["data"]["question"] = database.GetRandomQuestion("korona")
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
        for client in self.games[self.token]["clients"]:
            if "lost" in self.games[self.token]["data"]["finished"]:
                game = self.games[self.token]["data"]
            elif "won" in self.games[self.token]["data"]["finished"]:
                game = self.games[self.token]["data"]
            elif client.get_cookie("nejvyzkum-player") == self.games[self.token]["data"]["detective"]:
                game = copy.deepcopy(self.games[self.token]["data"])
                del game["criminal"]
            else:
                game = self.games[self.token]["data"]

            json = tornado.escape.json_encode(game)
            client.write_message(json)

def GetKoronaResults(personID: int) -> list:
    """
    Gets results for all questions for corona questionaire. Returns a list of questions (dicts). 
    """
    questions = database.GetAllTestQuestions("korona")
    for question in questions:
        question["rating"] = database.GetAnswerAverage(personID, question["id"])

    return questions
