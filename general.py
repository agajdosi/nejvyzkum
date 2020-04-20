import tornado.web
import settings

class GeneralHandler(tornado.web.RequestHandler):
    def enforceSSL(self):
        if settings.args.ssl == True and self.request.protocol == "http":
            self.redirect('https://' + self.request.host, permanent=False)
            return True

        return False
