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
        self.render("index.html", subtitle="Nejlepší z možných výzkumů")

class NotFound(general.GeneralHandler):
    def get(self):
        self.render("404.html")

def make_app():
    return tornado.web.Application([
        (r"/", Index),

        (r"/sedma-trida", sedma.Index),
        (r"/sedma-trida/hrat", sedma.Main),
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
