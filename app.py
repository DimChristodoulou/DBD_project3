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
    # Create a new connection
    # Create a new connection
    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()

    l_text = []
    l_negterms = []
    l_posterms = []

    cu = cur.execute('select var("arg",?)', (reviewid,))
    
    cu_txt = cur.execute('select textwindow(text,0,0,3) from reviews where var("arg")')

    j = 0
    for i in cu_txt:
        l_text.append(i)

    cu_negterms = cur.execute('select word from negterms')

    for i in cu_negterms:
        l_negterms.append(i[0])

    sum_neg = 0
    i = 0
    temp = ""
    while i < len(l_text):
        flag = 0
        if i % 3 == 0:
            temp = ""
        for negterm in l_negterms:
            found = l_text[i][0].find(negterm)
            if found != -1:
                if temp.find(negterm) == -1:
                    sum_neg += len(negterm.split())
                    temp = temp + " " + negterm
        i += 1

    cu_posterms = cur.execute('select word from posterms')

    for i in cu_posterms:
        l_posterms.append(i[0])

    sum_pos = 0
    i = 0
    temp = ""

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

    cu_name = cur.execute('select name from reviews, business where reviews.business_id = business.business_id and review_id = ?', myargs2)

    name = cu_name.fetchone()[0]

    print sum_neg, '|', sum_pos

    if sum_neg >= sum_pos:
        result = "negative"
    else:
        result = "positive"

    return [("business_name", "result"), (name, result)]


def classify_review_plain_sql(reviewid):
    # Create a new connection
    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()

    myargs1 = (reviewid,)

    cu_txt = cur.execute('select text from reviews where review_id = ?', myargs1)

    text = cu_txt.fetchone()[0]

    # print text
    l_text = []
    l_text = text.split()

    l_negterms = []
    l_posterms = []

    # print l_text

    cu_negterms = cur.execute('select word from negterms')

    for i in cu_negterms:
        l_negterms.append(i[0])

    sum_neg = 0
    temp = ""
    i = 0

    while i < len(l_text):
        if (i + 2) < len(l_text):
            curr_string = l_text[i] + " " + l_text[i + 1] + " " + l_text[i + 2]
        elif (i + 1) < len(l_text):
            curr_string = l_text[i] + " " + l_text[i + 1]
        else:
            curr_string = l_text[i]

        if i % 3 == 0:
            temp = ""

        for negterm in l_negterms:
            found = curr_string.find(negterm)
            if found != -1:
                if temp.find(negterm) == -1:
                    sum_neg += len(negterm.split())
                    temp = temp + " " + negterm
        i += 1

    cu_posterms = cur.execute('select word from posterms')

    for i in cu_posterms:
        l_posterms.append(i[0])

    sum_pos = 0
    temp = ""
    i = 0

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

    cu_name = cur.execute('select name from reviews, business where reviews.business_id = business.business_id and review_id = ?', myargs2)

    name = cu_name.fetchone()[0]

    print sum_neg, '|', sum_pos

    if sum_neg >= sum_pos:
        result = "negative"
    else:
        result = "positive"

    return [("business_name", "result"), (name, result)]


def updatezipcode(business_id, zipcode):
    # Create a new connection

    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()

    myargs1 = (zipcode, business_id)
    myargs2 = (business_id, zipcode)

    cur.execute("UPDATE business SET zip_code=? WHERE business_id=?", myargs1)

    newcur = con.cursor()
    newcur.execute("select exists(SELECT business_id FROM business WHERE business_id=? and zip_code=?)", myargs2)
    data = newcur.fetchone()
    if data == (0,):
        return [("result",), ('error',)]
    else:
        return [("result",), ('ok',)]


def selectTopNbusinesses(category_id, n):
    # Create a new connection

    con = connection()
    tu = ()
    narg = (category_id, n,)

    # Create a cursor on the connection
    cur = con.cursor()
    cu = cur.execute("SELECT b.business_id, count(rpn.positive) "
                     "FROM business b,business_category bc,category c, reviews r, reviews_pos_neg rpn "
                     "WHERE b.business_id = bc.business_id and bc.category_id = c.category_id and c.category_id = ? and "
                     "b.business_id = r.business_id and r.review_id = rpn.review_id "
                     "GROUP BY b.business_id "
                     "ORDER BY count(rpn.positive) DESC "
                     "LIMIT ?;", narg)

    l = []
    for i in cu:
        tu += i

    print l

    print tu

    return [("business_id", "numberOfreviews"), tu]


def traceUserInfuence(userId, depth):
    # Create a new connection
    con = connection()
    # Create a cursor on the connection
    cur = con.cursor()

    user_ids = []
    business_ids = []
    k = -1
    depthcounter = 1
    arg1 = (userId,)

    while k < len(user_ids):
        print depthcounter
        if k == -1:

            cu = cur.execute('SELECT f.friend_id, r1.business_id '
                             'FROM user u1, user u2, reviews r1, reviews r2, friends f '
                             'WHERE u1.user_id = ? and u1.user_id = f.user_id and u2.user_id = f.friend_id and '
                             'u1.user_id = r1.user_id and u2.user_id = r2.user_id and '
                             'r1.business_id = r2.business_id and r1.date < r2.date', arg1)

        else:
            if depthcounter <= int(depth):
                myargs = (user_ids[k], business_ids[k])
                print user_ids[k], business_ids[k]
                cu = cur.execute('SELECT f.friend_id, r1.business_id '
                                 'FROM user u1, user u2, reviews r1, reviews r2, friends f '
                                 'WHERE u1.user_id = ? and u1.user_id = f.user_id and u2.user_id = f.friend_id and '
                                 'u1.user_id = r1.user_id and u2.user_id = r2.user_id and '
                                 'r1.business_id = r2.business_id and r1.business_id = ? and r1.date < r2.date', myargs)
            else:
                break

        print "AFTER QUERY"

        for j in cu:
            user_ids.append(j[0])
            business_ids.append(j[1])

        depthcounter += 1
        k += 1

    tu = tuple(user_ids)

    return [("user_id",), tu]
