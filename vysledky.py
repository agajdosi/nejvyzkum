import random
import general, database, sedma, korona


class Vysledky(general.GeneralHandler):
    def get(self):
        if self.enforceSSL():
            return

        order = self.get_argument("order", "default")
        question = self.get_argument("question", None)
        lst = self.get_argument("list", "F19")
        lists = database.GetAllLists()
        
        if order == "default":
            persons = database.GetAllPersonsInList(lst)
        else:
            persons = database.GetAllPersonsInList(lst, onlyActive=True)

        questions = database.GetAllTestQuestions("korona")

        maximum = None
        minimum = None
        for i, person in enumerate(persons):
            if order == "default":
                break
            elif order == "questions" and question != None:
                person["score"] = database.GetAnswerAverage(person["id"], int(question))
                minimum = 0
                maximum = 1
            elif order in [
                    "extroversion",
                    "agreeableness",
                    "conscientiousness",
                    "neuroticism",
                    "openness",
                    "somatization",
                    "obsessiveCompulsive",
                    "interpersonalSensitivity",
                    "depression",
                    "anxiety",
                    "hostility",
                    "phobicAnxiety",
                    "paranoidIdeation",
                    "psychoticism",
                    "general",
                    ]:
                score = sedma.getTrait(person["id"], order)
                person["score"] = score
                if maximum == None:
                    maximum = score
                    minimum = score
                    continue
                if maximum < score:
                    maximum = score
                if minimum > score:
                    minimum = score
            else:
                self.redirect("404.html")

        if order != "default":
            persons.sort(key=lambda x: x.get('score'), reverse=True)

        return self.render("vysledky/vysledky.html",
            subtitle = "Výsledky výzkumu",
            persons = persons,
            maximum = maximum,
            minimum = minimum,
            selectedList = lst,
            order = order,
            lists = lists,
            questions = questions,
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
