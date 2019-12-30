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

        cursor = conn.execute("SELECT * FROM questions WHERE id IN (SELECT id FROM questions ORDER BY RANDOM() LIMIT 1)")
        question = cursor.fetchone()

        conn.close()
        random.shuffle(duo)
        self.render("play.html", subtitle="Play", first=duo[0], second=duo[1], question=question)

    def post(self):
        question = self.get_argument("question")
        yes = self.get_argument("yes")
        no = self.get_argument("no")
        
        # save here to the database
        print("TBD: save to DB:", question, yes, no)

        self.redirect("/play")

class Results(tornado.web.RequestHandler):
    def get(self):
        self.render("results.html", subtitle="Results")

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
