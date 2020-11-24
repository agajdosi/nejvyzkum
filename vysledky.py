import random
import general, database, sedma, korona


class Vysledky(general.GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return

        order = self.get_argument("order", "default")
        lst = self.get_argument("list", "F19")
        lists = database.GetAllLists()
        
        if order == "default":
            persons = database.GetAllPersonsInList(lst)
        else:
            persons = database.GetAllPersonsInList(lst, onlyActive=True)

        for i, person in enumerate(persons):
            if order == "default":
                break
            if order in ["extroversion", "agreeableness", "conscientiousness", "neuroticism", "openness"]:
                person["score"] = sedma.getTrait(person["id"], order)
            elif order in ["somatization", "obsessiveCompulsive", "interpersonalSensitivity", "depression", "anxiety", "hostility", "phobicAnxiety", "paranoidIdeation", "psychoticism", "general"]:
                person["score"] = sedma.getTrait(person["id"], order)

        if order != "default":
            persons.sort(key=lambda x: x.get('score'), reverse=True)

        return self.render("vysledky/vysledky.html",
            subtitle = "Výsledky výzkumu",
            persons = persons,
            selectedList = lst,
            lists = lists,
            url = self.request.full_url(),
        )

class Profil(general.GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return

        personID = self.get_argument("id", default=None)
        if personID == None:
            return self.redirect("/profil?id={}".format(random.randint(1,99)))

        personID = int(personID)

        person = database.GetPerson(personID)
        if person == None or person["active"] == 0:
            return self.redirect("/profil?id={}".format(random.randint(1,99)))

        bigFive = sedma.getBigFive(personID)
        scl90 = sedma.getSCL90(personID)
        koronaResults = korona.GetKoronaResults(personID)

        return self.render("vysledky/profil.html",
            subtitle="Profil",
            profile=person,
            bigFive=bigFive,
            scl90=scl90,
            korona=koronaResults,
            url=self.request.full_url(),
        )
