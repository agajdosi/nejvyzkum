import sqlite3, random

def parsePersonRow(row):
    profile = {"id":row[0], "active":row[1], "name":row[2], "image":row[3], "quote": row[4]}
    return profile

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
