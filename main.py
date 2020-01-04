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

def make_app():
    return tornado.web.Application([
        (r"/", Index),
        (r"/play", Play),
        (r"/results", Results),  

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
