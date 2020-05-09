import sqlite3, random

def parsePersonRow(row):
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

def parseQuestion(row):
    question = {
        "id": row[0],
        "eng-pre": row[1],
        "eng": row[2],
        "cz-pre": row[3],
        "cz": row[4],
        "test": row[5],
    }
    return question


def getPerson(personID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM persons WHERE id = '{0}'".format(personID))

    return parsePersonRow(cursor.fetchone())

def getRandomPersons(count):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM persons WHERE id IN (SELECT id FROM persons WHERE active = 1 ORDER BY RANDOM() LIMIT {0})".format(str(count)))
    rows = cursor.fetchall()

    profiles = []
    for row in rows:
        profiles.append(parsePersonRow(row))

    random.shuffle(profiles)
    return profiles

def getRandomQuestion(type):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM questions WHERE id IN (SELECT id FROM questions WHERE test = '{0}' ORDER BY RANDOM() LIMIT 1)".format(type))
    row = cursor.fetchone()

    return parseQuestion(row)
