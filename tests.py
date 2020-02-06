import sqlite3

def getBigFive(personID):
    rs = getAllQuestionRatings(personID, "bigfive")
    personality = {}
    personality["extroversion"] = 20 + rs[0] - rs[5] + rs[10] - rs[15] + rs[20] - rs[25] + rs[30] - rs[35] + rs[40] - rs[45]
    personality["agreeableness"] = 14 - rs[1] + rs[6] - rs[11] + rs[16] - rs[21] + rs[26] - rs[31] + rs[36] + rs[41] + rs[46]
    personality["conscientiousness"] = 14 + rs[2] - rs[7] + rs[12] - rs[17] + rs[22] - rs[27] + rs[32] - rs[37] + rs[42] + rs[47]
    personality["neuroticism"] = 38 - rs[3] + rs[8] - rs[13] + rs[18] - rs[23] - rs[28] - rs[33] - rs[38] - rs[43] - rs[48]
    personality["openness"] =  8 + rs[4] - rs[9] + rs[14] - rs[19] + rs[24] - rs[29] + rs[34] + rs[39] + rs[44] + rs[49]

    personality["average"] = (personality["extroversion"] + personality["agreeableness"] + personality["conscientiousness"] + personality["neuroticism"] + personality["openness"]) / 5

    return personality

def getTestQuestionIDs(test):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT (id) FROM questions WHERE test = '{0}'".format(test))
    IDs = cursor.fetchall()

    testIDs = []
    for ID in IDs:
        testIDs.append(ID[0])
    
    return testIDs

def getAllQuestionRatings(personID, testName):
    IDs = getTestQuestionIDs(testName)

    ratings = []
    for questionID in IDs:
        rating = getQuestionRating(personID, questionID)
        if rating < 0.2:
            rating = 1
        elif rating < 0.4:
            rating = 2
        elif rating < 0.6:
            rating = 3
        elif rating < 0.8:
            rating = 4
        elif rating < 1.0:
            rating = 5

        ratings.append(rating) #has to be in interval 1-5

    return ratings

def getQuestionRating(personID, questionID):
    conn = sqlite3.connect('prod.db')
    cursor = conn.execute("SELECT * FROM answers WHERE person = '{0}' AND  question = '{1}'".format(personID, questionID))
    answers = cursor.fetchall()
    if len(answers) == 0:
        return 0.5

    yes, no = 0, 0
    for answer in answers:
        if answer[3] == 1:
            yes = yes + 1
        elif answer[3] == 0:
            no = no + 1
        else:
            pass #wrong data, do not count
    
    rating = yes/(yes+no)
    return rating
