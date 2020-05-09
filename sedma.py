import sqlite3, random
import general, database

class Index(general.GeneralHandler):
    def get(self):
        person = database.getRandomPersons(1)[0]

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

        return self.render("sedma/index.html", subtitle="Nejlepší z možných výzkumů!", question=question)
    

class Main(general.GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return
        
        duo = database.getRandomPersons(2)

        conn = sqlite3.connect('prod.db')
        cursor = conn.execute("SELECT * FROM questions WHERE id IN (SELECT id FROM questions ORDER BY RANDOM() LIMIT 1)")
        question = cursor.fetchone()

        conn.close()
        return self.render("sedma/hrat.html", subtitle="Sedmá třída: Dotazník", first=duo[0], second=duo[1], question=question)

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
        person = database.getRandomPersons(1)[0]

        conn = sqlite3.connect('prod.db')
        cursor = conn.execute("SELECT question, answer FROM answers WHERE person = {0} AND question = (SELECT question FROM answers WHERE person = {0})".format(person["id"]))
        rows = cursor.fetchall()
        
        questionID = rows[0][0]
        yes = 0
        no = 0
        for row in rows:
            if row[1] == 1:
                yes = yes + 1
            else:
                no = no + 1

        answer = ""
        if yes >= no:
            answer = str(100*yes/(yes+no)) + "% lidí si myslí, že ANO!"
        else:
            answer = str(100*no/(yes+no)) + "% lidí si myslí, že NE!"
        
        cursor = conn.execute("SELECT cz FROM questions WHERE id = {0}".format(questionID))
        row = cursor.fetchone()

        question = person["name"] + " " + row[0]

        self.render("sedma/zajimavost.html", question=question, answer=answer, subtitle="Sedmá třída: Zajímavost")

class Profil(general.GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return
        
        personID = self.get_argument("id", default=None)
        if personID == None:
            return self.redirect("/sedma-trida/profil?id={}".format(random.randint(1,99)))

        person = database.getPerson(personID)
        if person["active"] == 0:
            return self.redirect("/sedma-trida/profil?id={}".format(random.randint(1,99)))

        bigFive, scl90 = getResults(personID)

        return self.render("sedma/profil.html", subtitle="Profil", profile=person, bigFive=bigFive, scl90=scl90)


def getResults(personID):
    bigFive = getBigFive(personID)
    scl90 = getSCL90(personID)

    return (bigFive, scl90)

def getLinks():
    """
    Generates links to next and previous profiles.
    """
    return

def getBigFive(personID):
    rs = getAllQuestionRatings(personID, "bigfive")
    bigFive = {}
    bigFive["extroversion"] = 20 + rs[0] - rs[5] + rs[10] - rs[15] + rs[20] - rs[25] + rs[30] - rs[35] + rs[40] - rs[45]
    bigFive["agreeableness"] = 14 - rs[1] + rs[6] - rs[11] + rs[16] - rs[21] + rs[26] - rs[31] + rs[36] + rs[41] + rs[46]
    bigFive["conscientiousness"] = 14 + rs[2] - rs[7] + rs[12] - rs[17] + rs[22] - rs[27] + rs[32] - rs[37] + rs[42] + rs[47]
    bigFive["neuroticism"] = 38 - rs[3] + rs[8] - rs[13] + rs[18] - rs[23] - rs[28] - rs[33] - rs[38] - rs[43] - rs[48]
    bigFive["openness"] =  8 + rs[4] - rs[9] + rs[14] - rs[19] + rs[24] - rs[29] + rs[34] + rs[39] + rs[44] + rs[49]

    bigFive["average"] = (bigFive["extroversion"] + bigFive["agreeableness"] + bigFive["conscientiousness"] + bigFive["neuroticism"] + bigFive["openness"]) / 5

    return bigFive

def getSCL90(personID):
    rs = getAllQuestionRatings(personID, "scl90")
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

def getTestQuestionIDs(test):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT (id) FROM questions WHERE test = '{0}'".format(test))
    IDs = cursor.fetchall()

    testIDs = []
    for ID in IDs:
        testIDs.append(ID[0])
    
    return testIDs

def getAllQuestionRatings(personID, testName):
    IDs = getTestQuestionIDs(testName)
    ratings = []
    for questionID in IDs:
        rating = getQuestionRating(personID, questionID)
        if testName == "bigfive":
            rating = bigFiveQoef(rating)
        elif testName == "scl90":
            rating = scl90Qoef(rating)
        ratings.append(rating)

    return ratings

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
    if rating < 0.3:
        rating = 0
    elif rating < 0.6:
        rating = 1
    elif rating < 0.8:
        rating = 2
    elif rating < 0.9:
        rating = 3
    elif rating <= 1.0:
        rating = 4
    
    return rating

def getQuestionRating(personID, questionID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT answer FROM answers WHERE person = '{0}' AND  question = '{1}'".format(personID, questionID))
    rows = cursor.fetchall()
    if len(rows) == 0:
        return 0.5

    answers = []
    for row in rows:
        answers.append(row[0])

    rating = sum(answers)/len(answers)
    rating = (rating + 1) / 2
    print(rating)
    return rating
