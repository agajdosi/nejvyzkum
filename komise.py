import general

class Komise(general.GeneralHandler):
  def get(self):
    if self.enforceSSL():
      return

    print(self.request.headers)

    return self.render("komise/komise.html",
      headers=self.request.headers,
    )
