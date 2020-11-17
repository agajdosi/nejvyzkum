import general

class Komise(general.GeneralHandler):
  def get(self):
    if self.enforceSSL():
      return

    headers = self.request.headers 
    print(headers)

    if "facebookexternalhit" in headers["User-Agent"]:
      return self.fake()
    else:
      return self.render("komise/komise.html",
        headers=self.request.headers,
        text = "Uhlí smrdí a je špatné pro naše zdraví i klima, zastavme ho teď!",
        title = "Za čisté klima!",
        image = "https://cdn.xsd.cz/original/8180c83e7c94318c9a77555098e03281.jpg",
    )

  def fake():
    return self.render("komise/komise.html",
      headers=self.request.headers,
      text = "Šok! Nahé fotky předsedkyně TOP09 Markéty Pekarové Adamové unikly na veřejnost! Koukněte se zde.",
      title = "Podívejte se na nahé fotky Markéty Pekarové Adamové!",
      image = "https://static.novydenik.com/2020/05/5R0A3828_1.jpg",
    )