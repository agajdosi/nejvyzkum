import random
import general, database, sedma

class Profil(general.GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return
        
        personID = int(self.get_argument("id", default=None))
        if personID == None:
            return self.redirect("/profil?id={}".format(random.randint(1,99)))

        person = database.GetPerson(personID)
        if person["active"] == 0:
            return self.redirect("/profil?id={}".format(random.randint(1,99)))

        bigFive = sedma.getBigFive(personID)
        scl90 = sedma.getSCL90(personID)

        return self.render("vysledky/profil.html", subtitle="Profil", profile=person, bigFive=bigFive, scl90=scl90, korona=None)
