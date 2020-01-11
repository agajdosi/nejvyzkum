import sqlite3
from bigfive import getBigFive

def getProfile(personID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT name, image FROM persons WHERE id = '{0}'".format(personID))
    row = cursor.fetchone()
    profile = {"id":personID, "name":row[0], "image":row[1]}

    #for now the BigFive is default and only test used
    personality = getBigFive(personID)

    return (profile, personality)

def getLinks():
    """
    Generates links to next and previous profiles.
    """
    return
