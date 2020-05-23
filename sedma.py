import sqlite3, random
import general, database

class Index(general.GeneralHandler):
    def get(self):
        person = database.GetRandomPersons(1)[0]

        questions = [
            "Je * samotář?",
            "Je * introvert?",
            "Je * agresivní?",
            "Je * psychopat?",
            "Je * sociopat?",
            "Je * zlý?",
            "Je * necita?"
        ]

        question = random.choice(questions)
        question = question.replace("*", person["name"])

        return self.render("sedma/index.html",
            subtitle="Nejlepší z možných výzkumů!",
            question=question,
            url=self.request.full_url(),
        )

class Main(general.GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return
        
        duo = database.GetRandomPersons(2)
        question = database.GetRandomQuestion(["scl90", "bigfive"])

        return self.render("sedma/hrat.html",
            subtitle="Sedmá třída: Dotazník",
            first=duo[0],
            second=duo[1],
            question=question,
            url=self.request.full_url(),
        )

    def post(self):
        question = int(self.get_argument("question"))
        yesPerson = int(self.get_argument("yes"))
        noPerson = int(self.get_argument("no"))

        database.InsertAnswer(question, 1.0, yesPerson, noPerson)
        database.InsertAnswer(question, -1.0, noPerson, yesPerson)

        x = random.random()
        if x > 0.90:
            return self.redirect("/sedma-trida/zajimavost")
        else:
            return self.redirect("/sedma-trida/hrat")

class Zajimavost(general.GeneralHandler):
    def get(self):
        person = database.GetRandomPersons(1)[0]
        question = database.GetRandomQuestion(["scl90", "bigfive"])
        average = database.GetAnswerAverage(person["id"],question["id"])

        questionText = person["name"] + " " + question["cz"]
        answerText = ""
        if average >= 0.5:
            answerText = str(average*100) + "% lidí si myslí, že ANO!"
        else:
            answerText = str((1-average)*100) + "% lidí si myslí, že NE!"
        
        self.render("sedma/zajimavost.html",
            question=questionText,
            answer=answerText,
            subtitle="Sedmá třída: Zajímavost",
            url=self.request.full_url(),
        )

def getBigFive(personID):
    questions = database.GetAllTestQuestions("bigfive")
    rs = []
    for question in questions:
        rating = database.GetAnswerAverage(personID, question["id"])
        rating = bigFiveQoef(rating)
        rs.append(rating)

    bigFive = {}
    bigFive["extroversion"] = 20 + rs[0] - rs[5] + rs[10] - rs[15] + rs[20] - rs[25] + rs[30] - rs[35] + rs[40] - rs[45]
    bigFive["agreeableness"] = 14 - rs[1] + rs[6] - rs[11] + rs[16] - rs[21] + rs[26] - rs[31] + rs[36] + rs[41] + rs[46]
    bigFive["conscientiousness"] = 14 + rs[2] - rs[7] + rs[12] - rs[17] + rs[22] - rs[27] + rs[32] - rs[37] + rs[42] + rs[47]
    bigFive["neuroticism"] = 38 - rs[3] + rs[8] - rs[13] + rs[18] - rs[23] - rs[28] - rs[33] - rs[38] - rs[43] - rs[48]
    bigFive["openness"] =  8 + rs[4] - rs[9] + rs[14] - rs[19] + rs[24] - rs[29] + rs[34] + rs[39] + rs[44] + rs[49]

    bigFive["average"] = (bigFive["extroversion"] + bigFive["agreeableness"] + bigFive["conscientiousness"] + bigFive["neuroticism"] + bigFive["openness"]) / 5

    return bigFive

def getSCL90(personID):
    questions = database.GetAllTestQuestions("scl90")
    rs = []
    for question in questions:
        rating = database.GetAnswerAverage(personID, question["id"])
        rating = scl90Qoef(rating)
        rs.append(rating)

    scl90 = {}
    scl90["somatization"] = (rs[0] + rs[3] + rs[11] + rs[26] + rs[39] + rs[41] + rs[47] + rs[48] + rs[51] + rs[52] + rs[55] + rs[57] ) / 12
    scl90["obsessiveCompulsive"] = (rs[2] + rs[8] + rs[9] + rs[27] + rs[37] + rs[44] + rs[45] + rs[50] + rs[54] + rs[64]) / 10
    scl90["interpersonalSensitivity"] = (rs[5] + rs[20] + rs[33] + rs[35] + rs[36] + rs[40] + rs[60] + rs[68] + rs[72]) / 9
    scl90["depression"] = (rs[4] + rs[13] + rs[14] + rs[19] + rs[21] + rs[25] + rs[28] + rs[29] + rs[30] + rs[31] + rs[53] + rs[70] + rs[78]) / 13
    scl90["anxiety"] = (rs[1] + rs[16] + rs[22] + rs[32] + rs[38] + rs[56] + rs[71] + rs[77] + rs[79] + rs[85]) / 10
    scl90["hostility"] = (rs[10] + rs[23] + rs[62] + rs[66] + rs[73] + rs[80]) / 6
    scl90["phobicAnxiety"] = (rs[12] + rs[24] + rs[46] + rs[49] + rs[69] + rs[74] + rs[81]) / 7
    scl90["paranoidIdeation"] = (rs[7] + rs[17] + rs[42] + rs[67] + rs[75] + rs[82]) / 6
    scl90["psychoticism"] = (rs[6] + rs[15] + rs[34] + rs[61] + rs[76] + rs[83] + rs[84] + rs[86] + rs[87] + rs[89]) / 10
    scl90["general"] = sum(rs) / 90
    
    return scl90

def bigFiveQoef(rating):
    if rating < 0.2:
        rating = 1
    elif rating < 0.4:
        rating = 2
    elif rating < 0.6:
        rating = 3
    elif rating < 0.8:
        rating = 4
    elif rating <= 1.0:
        rating = 5
    
    return rating

def scl90Qoef(rating):
    if rating <= 0.5:
        rating = 0
    elif rating < 0.7:
        rating = 1
    elif rating < 0.8:
        rating = 2
    elif rating < 0.95:
        rating = 3
    elif rating <= 1.0:
        rating = 4
    
    return rating
