import sqlite3, random


### TABLE: persons

def parsePersonRow(row: list) -> dict:
    """
    Parses a list of all rows in persons table into a named dictionary.
    """
    profile = {
        "id":row[0],
        "active":row[1],
        "name":row[2],
        "image":row[3],
        "quote": row[4],
        "quote-en": row[5],
        "mainsource": row[6],
        "mainsource-en": row[7],
        "sidesource": row[8],
        "sidesource-en": row[9],
        "birthday": row[10],
        "residence": row[11],
        "residence-en": row[12],
        "birthplace": row[13],
        "birthplace-en": row[14],
        "education": row[15],
        "education-en": row[16],
        "maritalstatus": row[17],
        "maritalstatus-en": row[18],
        "children": row[19],
        "obsession": row[20],
        "obsession-en": row[21],
        "car": row[22],
        "maincompany": row[23],
        "maincompany-en": row[24],
        "sidecompanies": row[25],
        "sidecompanies-en": row[26],
        "wealthorigin": row[27],
        "wealthorigin-en": row[28],
        "wealth": row[29],
        "wealth-en": row[30],
    }
    return profile

def GetPerson(personID: int) -> dict:
    """
    Gets person of selected ID from the database. Returns a dict containing all data available for the person.
    """
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM persons WHERE id = '{0}'".format(personID))
    row = cursor.fetchone()

    if row == None:
        return None
    
    return parsePersonRow(row)

def GetExistingPerson(personID: int, step: int=1):
    """
    Gets existing person from database. Of person is not active, it tries person next to it - based on step length. 
    """
    while True:
        person = GetPerson(personID)
        if person == None:
            # ugly: should get number of persons from DB
            if personID < 1:
                personID = 100
            else:
                personID = 1
            continue

        if person["active"] == 1:
            return person

        personID = personID + step

def GetRandomPersons(count: int) -> list:
    """
    Gets list of N random persons from the database. Returned value is a list containing dict of all data available for the person.
    """
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM persons WHERE id IN (SELECT id FROM persons WHERE active = 1 ORDER BY RANDOM() LIMIT {0})".format(str(count)))
    rows = cursor.fetchall()

    profiles = []
    for row in rows:
        profiles.append(parsePersonRow(row))

    random.shuffle(profiles)
    return profiles

### TABLE: questions

def parseQuestionRow(row: list) -> dict:
    """
    Parses a list of all rows in question table into a named dictionary.
    """
    question = {
        "id": row[0],
        "eng-pre": row[1],
        "eng": row[2],
        "cz-pre": row[3],
        "cz": row[4],
        "test": row[5],
    }
    return question

def GetRandomQuestion(test: str) -> dict:
    """
    Gets random question from database for selected test.
    """
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM questions WHERE id IN (SELECT id FROM questions WHERE test = '{0}' ORDER BY RANDOM() LIMIT 1)".format(test))
    row = cursor.fetchone()

    return parseQuestionRow(row)

def GetAllTestQuestions(test: str) -> list:
    """
    Gets list of all questions for selected type of the test.
    """
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM questions WHERE test = '{0}'".format(test))
    rows = cursor.fetchall()

    questions = []
    for row in rows:
        question = parseQuestionRow(row)
        questions.append(question)
    
    return questions


### TABLE: answers

def GetAnswerAverage(personID: int, questionID: int) -> float:
    """
    Gets average answer for selected person and question. Returned value is between 0 (100% NO) and 1.0 (100% YES).
    """
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT answer FROM answers WHERE person = '{0}' AND  question = '{1}'".format(personID, questionID))
    rows = cursor.fetchall()
    if len(rows) == 0:
        return 0.5

    answers = []
    for row in rows:
        answers.append(row[0])

    rating = sum(answers)/len(answers)
    rating = (rating + 1) / 2.0

    return rating

def InsertAnswer(question: int, answer: float, who: int, versus: int) -> None:
    """
    Inserts an answer into a database. Answer should be between -1.0 (100% NO) and 1.0 (100% YES).
    """
    conn = sqlite3.connect('prod.db')
    conn.execute("INSERT INTO answers (question, person, answer, versus) VALUES ('{0}', '{1}', '{2}', '{3}')".format(question, who, answer, versus))
    conn.commit()
    conn.close()
