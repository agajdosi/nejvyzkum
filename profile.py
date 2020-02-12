import sqlite3
from tests import getBigFive, getSCL90

def getProfile(personID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT name, active, image, quote FROM persons WHERE id = '{0}'".format(personID))
    row = cursor.fetchone()
    quote = row[3]
    if quote != None:
        quote = "„" + row[3] + "“"
    else:
        quote = ""
    profile = {"id":personID, "name":row[0], "active":row[1], "image":row[2], "quote": quote}

    return profile

def getResults(personID):
    bigFive = getBigFive(personID)
    scl90 = getSCL90(personID)

    return (bigFive, scl90)

def getLinks():
    """
    Generates links to next and previous profiles.
    """
    return
