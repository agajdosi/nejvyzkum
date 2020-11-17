import tornado.ioloop, tornado.web
import sqlite3, random
import sedma, korona, vysledky, general, settings, komise

class Index(general.GeneralHandler):
    def get(self):
        self.render("index.html",
            subtitle="Nejlepší z možných výzkumů",
            url=self.request.full_url(),
        )

class NotFound(general.GeneralHandler):
    def get(self):
        self.render("404.html", url=self.request.full_url())

def make_app():
    return tornado.web.Application([
        (r"/", Index),
        (r"/profil/?", vysledky.Profil),
        (r"/vysledky/?", vysledky.Vysledky),
        (r"/komise/?", komise.Komise),


        (r"/sedma-trida/?", sedma.Index),
        (r"/sedma-trida/hrat/?", sedma.Main),
        (r"/sedma-trida/zajimavost/?", sedma.Zajimavost),

        (r"/korona/?", korona.Index),
        (r"/korona/hra/(.{5,32})/?", korona.Hra),
        (r"/korona/ws/(.{5,32})/?", korona.WebSocket),

        (r'/js/(.*\.js)', tornado.web.StaticFileHandler, {'path': 'js/'}),
        (r'/css/(.*\.css)', tornado.web.StaticFileHandler, {'path': 'css/'}),
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
