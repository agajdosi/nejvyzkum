import tornado.ioloop
import tornado.web
import sqlite3


import argparse

class Index(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", subtitle="Index")

class Play(tornado.web.RequestHandler):
    def get(self):
        self.render("play.html", subtitle="Play")

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
