import tornado.ioloop
import tornado.web
import sqlite3
import random
import argparse

class Index(tornado.web.RequestHandler):
    def get(self):        
        self.render("index.html", subtitle="Index")

class Play(tornado.web.RequestHandler):
    def get(self):
        conn = sqlite3.connect('prod.db')
        cursor = conn.execute("SELECT * FROM persons WHERE id IN (SELECT id FROM persons ORDER BY RANDOM() LIMIT 2)")
        duo = cursor.fetchall()
        random.shuffle(duo)

        cursor = conn.execute("SELECT * FROM questions WHERE id IN (SELECT id FROM questions ORDER BY RANDOM() LIMIT 1)")
        question = cursor.fetchone()

        conn.close()
        self.render("play.html", subtitle="Play", first=duo[0], second=duo[1], question=question)

    def post(self):
        question = self.get_argument("question")
        yesPerson = self.get_argument("yes")
        noPerson = self.get_argument("no")

        conn = sqlite3.connect('prod.db')
        conn.execute("INSERT INTO answers (question, person, answer, versus) VALUES ('{0}', '{1}', '{2}', '{3}')".format(question, yesPerson, 1, noPerson))
        conn.execute("INSERT INTO answers (question, person, answer, versus) VALUES ('{0}', '{1}', '{2}', '{3}')".format(question, noPerson, 0, yesPerson))
        conn.commit()
        conn.close()

        self.redirect("/play")

class Results(tornado.web.RequestHandler):
    def get(self):
        # UGLY!! split to smaller functions
        conn = sqlite3.connect('prod.db')
        cursor = conn.execute("SELECT * FROM persons")

        persons = cursor.fetchall()

        stats = []
        for person in persons:
            personID = person[0]

            cursor = conn.execute("SELECT * FROM questions")
            questions = cursor.fetchall()

            for question in questions:
                questionID = question[0]
                cursor = conn.execute("SELECT * FROM answers WHERE person = '{0}' AND  question = '{1}'".format(personID, questionID))
                answers = cursor.fetchall()

                yes = 0
                no = 0
                for answer in answers:
                    if answer[3] == 1:
                        yes = yes + 1
                    else:
                        no = no + 1

                if yes+no == 0:
                    continue

                stats.append([person[1], question[1], 100*yes/(yes+no), 100*no/(yes+no)])

        conn.close()
        self.render("results.html", subtitle="Results", stats=stats)

class Profile(tornado.web.RequestHandler):
    def get(self):
        personID = self.get_argument("id", default=None)
        print(personID)
        if personID == None:
            self.redirect("/")

        personality = getPerson(personID)
        self.render("profile.html", subtitle="Profile", personality=personality)

def getPerson(personID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT id, name FROM persons WHERE id = '{0}'".format(personID))
    row = cursor.fetchone()
    
    personality = getBigFive(personID)
    personality["id"] = row[0]
    personality["name"] = row[1]

    return personality

def getQuestionRating(personID, questionID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM answers WHERE person = '{0}' AND  question = '{1}'".format(personID, questionID))
    answers = cursor.fetchall()
    if len(answers) == 0:
        return 0.5

    yes, no = 0, 0
    for answer in answers:
        if answer[3] == 1:
            yes = yes + 1
        elif answer[3] == 0:
            no = no + 1
        else:
            pass #wrong data, do not count
    
    rating = yes/(yes+no)
    return rating

def getAllQuestionRatings(personID):
    IDs = range(1,51) #fixed, we know we do Big5 which has 50 questions
    ratings = []
    for questionID in IDs:
        rating = getQuestionRating(personID, questionID)
        if rating < 0.2:
            rating = 1
        elif rating < 0.4:
            rating = 2
        elif rating < 0.6:
            rating = 3
        elif rating < 0.8:
            rating = 4
        elif rating < 1.0:
            rating = 5

        ratings.append(rating) #has to be in interval 1-5

    return ratings

def getBigFive(personID):
    rs = getAllQuestionRatings(personID)
    personality = {}
    personality["extroversion"] = 20 + rs[0] - rs[5] + rs[10] - rs[15] + rs[20] - rs[25] + rs[30] - rs[35] + rs[40] - rs[45]
    personality["agreeableness"] = 14 - rs[1] + rs[6] - rs[11] + rs[16] - rs[21] + rs[26] - rs[31] + rs[36] + rs[41] + rs[46]
    personality["conscientiousness"] = 14 + rs[2] - rs[7] + rs[12] - rs[17] + rs[22] - rs[27] + rs[32] - rs[37] + rs[42] + rs[47]
    personality["neuroticism"] = 38 - rs[3] + rs[8] - rs[13] + rs[18] - rs[23] - rs[28] - rs[33] - rs[38] - rs[43] - rs[48]
    personality["openness"] =  8 + rs[4] - rs[9] + rs[14] - rs[19] + rs[24] - rs[29] + rs[34] + rs[39] + rs[44] + rs[49]

    personality["average"] = (personality["extroversion"] + personality["agreeableness"] + personality["conscientiousness"] + personality["neuroticism"] + personality["openness"]) / 5

    return personality

def make_app():
    return tornado.web.Application([
        (r"/", Index),
        (r"/play", Play),
        (r"/results", Results),
        (r"/profile", Profile),

        (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': 'js/'}),
        (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'css/'}),
        (r'/img/(.*)', tornado.web.StaticFileHandler, {'path': 'img/'}),
    ],
    template_path = "templates",
    debug = True
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", help="defines which port will be used by webserver", type=int, default=8080)
    args = parser.parse_args()

    app = make_app()
    app.listen(args.port)

    print("server has started: http://localhost:" + str(args.port))
    tornado.ioloop.IOLoop.current().start()
