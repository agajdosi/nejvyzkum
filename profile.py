import sqlite3
from tests import getBigFive, getSCL90

def getProfile(personID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT name, active, image FROM persons WHERE id = '{0}'".format(personID))
    row = cursor.fetchone()
    profile = {"id":personID, "name":row[0], "active":row[1], "image":row[2]}

    #for now the BigFive is default and only test used
    bigFive = getBigFive(personID)
    scl90 = getSCL90(personID)

    return (profile, bigFive, scl90)

def getLinks():
    """
    Generates links to next and previous profiles.
    """
    return
