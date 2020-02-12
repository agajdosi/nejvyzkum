import tornado.ioloop
import tornado.web
import sqlite3
import random

import settings
import profile

class GeneralHandler(tornado.web.RequestHandler):
    def enforceSSL(self):
        if settings.args.ssl == True and self.request.protocol == "http":
            self.redirect('https://' + self.request.host, permanent=False)
            return True

        return False

class Index(GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return

        conn = sqlite3.connect('prod.db')
        cursor = conn.execute("SELECT name FROM persons WHERE id IN (SELECT id FROM persons WHERE active = 1 ORDER BY RANDOM() LIMIT 1)")
        name = cursor.fetchone()[0]

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
        question = question.replace("*", name)

        return self.render("index.html", subtitle="Nejlepší z možných výzkumů!", question=question)

class Play(GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return
        
        conn = sqlite3.connect('prod.db')
        cursor = conn.execute("SELECT * FROM persons WHERE id IN (SELECT id FROM persons WHERE active = 1 ORDER BY RANDOM() LIMIT 2)")
        duo = cursor.fetchall()
        random.shuffle(duo)

        cursor = conn.execute("SELECT * FROM questions WHERE id IN (SELECT id FROM questions ORDER BY RANDOM() LIMIT 1)")
        question = cursor.fetchone()

        conn.close()
        return self.render("play.html", subtitle="Dotazník", first=duo[0], second=duo[1], question=question)

    def post(self):
        question = self.get_argument("question")
        yesPerson = self.get_argument("yes")
        noPerson = self.get_argument("no")

        conn = sqlite3.connect('prod.db')
        conn.execute("INSERT INTO answers (question, person, answer, versus) VALUES ('{0}', '{1}', '{2}', '{3}')".format(question, yesPerson, 1, noPerson))
        conn.execute("INSERT INTO answers (question, person, answer, versus) VALUES ('{0}', '{1}', '{2}', '{3}')".format(question, noPerson, 0, yesPerson))
        conn.commit()
        conn.close()

        x = random.random()
        if x > 0.90:
            return self.redirect("/reward")
        else:
            return self.redirect("/play")

class Profile(GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return
        
        personID = self.get_argument("id", default=None)
        if personID == None:
            return self.redirect("/profile?id={}".format(random.randint(1,99)))

        person = profile.getProfile(personID)
        if person["active"] == 0:
            return self.redirect("/profile?id={}".format(random.randint(1,99)))

        bigFive, scl90 = profile.getResults(personID)

        return self.render("profile.html", subtitle="Profil", profile=person, bigFive=bigFive, scl90=scl90)

class Reward(GeneralHandler):
    def get(self):
        conn = sqlite3.connect('prod.db')
        cursor = conn.execute("SELECT id, name FROM persons WHERE id IN (SELECT id FROM persons WHERE active = 1 ORDER BY RANDOM() LIMIT 1)")
        row = cursor.fetchone()
        personID = row[0]
        name = row[1]

        cursor = conn.execute("SELECT question, answer FROM answers WHERE person = {0} AND question = (SELECT question FROM answers WHERE person = {0})".format(personID))
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

        question = name + " " + row[0]

        self.render("reward.html", question=question, answer=answer)

class NotFound(GeneralHandler):
    def get(self):
        self.render("404.html")

def make_app():
    return tornado.web.Application([
        (r"/", Index),
        (r"/play", Play),
        (r"/profile", Profile),
        (r"/reward", Reward),

        (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': 'js/'}),
        (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'css/'}),
        (r'/img/(.*)', tornado.web.StaticFileHandler, {'path': 'img/'}),
        (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': 'img/'}),
    ],
    template_path = "templates",
    debug = settings.args.debug,
    default_handler_class=NotFound
    )

if __name__ == "__main__":
    settings.init()

    app = make_app()
    app.listen(settings.args.port)


    if settings.args.ssl == True:
        app.listen(settings.args.sslport, ssl_options={
            "certfile": "/etc/letsencrypt/live/nejvyzkum.cz/fullchain.pem",
            "keyfile": "/etc/letsencrypt/live/nejvyzkum.cz/privkey.pem",
        })

    print("server has started: http://localhost:" + str(settings.args.port))
    tornado.ioloop.IOLoop.current().start()
