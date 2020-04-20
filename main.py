import tornado.ioloop
import tornado.web
import sqlite3
import random

import settings
import general
import profile
import sedma

class Index(general.GeneralHandler):
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

class NotFound(general.GeneralHandler):
    def get(self):
        self.render("404.html")

def make_app():
    return tornado.web.Application([
        (r"/", Index),

        (r"/sedma-trida", sedma.Main),
        (r"/sedma-trida/profil", sedma.Profil),
        (r"/sedma-trida/zajimavost", sedma.Zajimavost),

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
