# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys


def connection():
    ''' User this function to create your connections '''
    import sys
    sys.path.append(settings.MADIS_PATH)
    import madis

    con = madis.functions.Connection('yelp.db')

    return con


def classify_review(reviewid):
    # Create a new connection.
    con = connection()

    # Create a cursor on the connection.
    cur = con.cursor()

    l_text = []
    l_negterms = []
    l_posterms = []

    cur.execute('select var("arg",?)', (reviewid,))

    cu_txt = cur.execute(
        'select textwindow(text,0,0,3) from reviews where review_id = var("arg")')  # Take 3 words each time the middle pointer moves.

    j = 0
    for i in cu_txt:
        l_text.append(i)

    cu_negterms = cur.execute('select word from negterms')

    for i in cu_negterms:
        l_negterms.append(i[0])

    sum_neg = 0
    temp = ""
    i = 0
    # Calculate the count of negterms in text.
    while i < len(l_text):
        flag = 0
        if i % 3 == 0:  # Every three moves of middle pointer (from textwindow).
            temp = ""  # Reset temp variable.
        for negterm in l_negterms:
            found = l_text[i][0].find(negterm)
            if found != -1:  # If negterm was found in curr_string.
                if temp.find(
                        negterm) == -1:  # If negterm was not found in temp(it is not a part of an existing negterm).
                    sum_neg += len(negterm.split())  # Add the count of negterm's words to sum_neg.
                    temp = temp + " " + negterm
        i += 1

    cu_posterms = cur.execute('select word from posterms')

    for i in cu_posterms:
        l_posterms.append(i[0])

    sum_pos = 0
    temp = ""
    i = 0
    # Calculate the count of posterms in text in exactly the same way as above.
    while i < len(l_text):
        flag = 0
        if i % 3 == 0:
            temp = ""
        for posterm in l_posterms:
            found = l_text[i][0].find(posterm)
            if found != -1:
                if temp.find(posterm) == -1:
                    sum_pos += len(posterm.split())
                    temp = temp + " " + posterm
        i += 1

    myargs2 = (reviewid,)

    cu_name = cur.execute(
        'select name from reviews, business where reviews.business_id = business.business_id and review_id = ?',
        myargs2)

    name = cu_name.fetchone()[0]

    if sum_neg >= sum_pos:
        result = "negative"
    else:
        result = "positive"

    return [("business_name", "result"), [(name, result)]]


def classify_review_plain_sql(reviewid):
    # Create a new connection.
    con = connection()

    # Create a cursor on the connection.
    cur = con.cursor()

    myargs1 = (reviewid,)

    cu_txt = cur.execute('select text from reviews where review_id = ?', myargs1)

    text = cu_txt.fetchone()[0]  # Get only the string from the tuple.

    l_text = []
    l_text = text.split()  # Divide text into single words.

    l_negterms = []
    l_posterms = []

    cu_negterms = cur.execute('select word from negterms')

    for i in cu_negterms:
        l_negterms.append(i[0])

    sum_neg = 0
    temp = ""

    i = 0
    # Calculate the count of negterms in text.
    while i < len(l_text):
        # Implement the functionality of textwindow.
        if (i + 2) < len(l_text):
            curr_string = l_text[i] + " " + l_text[i + 1] + " " + l_text[i + 2]
        elif (i + 1) < len(l_text):
            curr_string = l_text[i] + " " + l_text[i + 1]
        else:
            curr_string = l_text[i]

        if i % 3 == 0:  # Every three words.
            temp = ""  # Reset temp variable.

        for negterm in l_negterms:
            found = curr_string.find(negterm)
            if found != -1:  # If negterm was found in curr_string.
                if temp.find(
                        negterm) == -1:  # If negterm was not found in temp(it is not a part of an existing negterm).
                    sum_neg += len(negterm.split())  # Add the count of negterm's words to sum_neg.
                    temp = temp + " " + negterm
        i += 1

    cu_posterms = cur.execute('select word from posterms')

    for i in cu_posterms:
        l_posterms.append(i[0])

    sum_pos = 0
    temp = ""

    i = 0
    # Calculate the count of posterms in text in exactly the same way as above.
    while i < len(l_text):

        if (i + 2) < len(l_text):
            curr_string = l_text[i] + " " + l_text[i + 1] + " " + l_text[i + 2]
        elif (i + 1) < len(l_text):
            curr_string = l_text[i] + " " + l_text[i + 1]
        else:
            curr_string = l_text[i]

        if i % 3 == 0:
            temp = ""

        for posterm in l_posterms:
            found = curr_string.find(posterm)
            if found != -1:
                if temp.find(posterm) == -1:
                    sum_pos += len(posterm.split())
                    temp = temp + " " + posterm
        i += 1

    myargs2 = (reviewid,)

    cu_name = cur.execute(
        'select name from reviews, business where reviews.business_id = business.business_id and review_id = ?',
        myargs2)

    name = cu_name.fetchone()[0]

    if sum_neg >= sum_pos:
        result = "negative"
    else:
        result = "positive"

    return [("business_name", "result"), [(name, result)]]


def updatezipcode(business_id, zipcode):
    # Create a new connection.
    con = connection()

    # Create a cursor on the connection.
    cur = con.cursor()

    myargs1 = (zipcode, business_id)
    myargs2 = (business_id, zipcode)
    # Tuples used for sqlinjection protection.

    cur.execute("UPDATE business SET zip_code=? WHERE business_id=?", myargs1)
    # Query used to update the zip_code row in the business array.

    newcur = con.cursor()
    newcur.execute("select exists(SELECT business_id FROM business WHERE business_id=? and zip_code=?)", myargs2)
    # Query used for the return statement.

    data = newcur.fetchone()[0]

    if data == 0:   # Didn't find a row with a zip_code equal to the zipcode argument, return error.
        return [("result",), [('error',)]]
    else:   # Found a row with a zip_code equal to the zipcode argument, return ok.
        return [("result",), [('ok',)]]


def selectTopNbusinesses(category_id, n):
    # Create a new connection.
    con = connection()

    # Create a cursor on the connection.
    cur = con.cursor()

    narg = (category_id, n,)
    cu = cur.execute("SELECT b.business_id, sum(rpn.positive) "
                     "FROM business b,business_category bc,category c, reviews r, reviews_pos_neg rpn "
                     "WHERE b.business_id = bc.business_id and bc.category_id = c.category_id and c.category_id = ? and "
                     "b.business_id = r.business_id and r.review_id = rpn.review_id "
                     "GROUP BY b.business_id "
                     "ORDER BY sum(rpn.positive) DESC "
                     "LIMIT ?;", narg)

    # This query selects the business id and the count of the positive reviews by adding one if the review is positive
    # or zero if it is negative. The query also orders the positive reviews in descending order and limits the statement
    # to return n (argument) businesses.

    l = []
    for i in cu:
        l.append(i)

    return [("business_id", "numberOfreviews"), l]


def traceUserInfuence(userId, depth):
    # Create a new connection.
    con = connection()

    # Create a cursor on the connection.
    cur = con.cursor()

    user_ids = []
    business_ids = []

    k = -1
    depthcounter = 1  # Current depth.
    arg1 = (userId,)

    while k < len(user_ids):

        if k == -1:  # First time in While loop.
            cu = cur.execute('SELECT f.friend_id, r1.business_id '
                             'FROM user u1, user u2, reviews r1, reviews r2, friends f '
                             'WHERE u1.user_id = ? and u1.user_id = f.user_id and u2.user_id = f.friend_id and '
                             'u1.user_id = r1.user_id and u2.user_id = r2.user_id and '
                             'r1.business_id = r2.business_id and r1.date < r2.date', arg1)

            # If k == -1 that means we want to search for the user's immediate friends.

        else:
            if depthcounter <= int(depth):
                myargs = (user_ids[k], business_ids[k])
                cu = cur.execute('SELECT f.friend_id, r1.business_id '
                                 'FROM user u1, user u2, reviews r1, reviews r2, friends f '
                                 'WHERE u1.user_id = ? and u1.user_id = f.user_id and u2.user_id = f.friend_id and '
                                 'u1.user_id = r1.user_id and u2.user_id = r2.user_id and '
                                 'r1.business_id = r2.business_id and r1.business_id = ? and r1.date < r2.date', myargs)

                # This query returns the ids of the friends that have depth > 1 (friend's friends)

            else:  # Depthcounter has gone past the given depth.
                break

        for j in cu:
            user_ids.append(j[0])  # Store found user ids.
            business_ids.append(j[1])  # Store found business ids.

        depthcounter += 1
        k += 1

    l = []
    for i in user_ids:
        l.append(tuple([i]))

    return [("user_id",), l]
