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

    return [("business_name", "result")]


def classify_review_plain_sql(reviewid):
    # Create a new connection
    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()

    return [("business_name", "result")]


def updatezipcode(business_id, zipcode):
    # Create a new connection

    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()
    cur.execute("UPDATE business SET zip_code='%s' WHERE business_id='%s'" % (zipcode, business_id))

    newcur = con.cursor()
    newcur.execute("select exists(SELECT business_id FROM business WHERE business_id='%s' and zip_code='%s')" % (
    business_id, zipcode))
    data = newcur.fetchone()
    if data == (0,):
        return [("result",), ('error',)]
    else:
        return [("result",), ('ok',)]


def selectTopNbusinesses(category_id, n):
    # Create a new connection

    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()
    cu = cur.execute("SELECT b.business_id, count(rpn.positive) "
                     "FROM business b,business_category bc,category c, reviews r, reviews_pos_neg rpn "
                     "WHERE b.business_id = bc.business_id and bc.category_id = c.category_id and c.category_id = %s and "
                     "b.business_id = r.business_id and r.review_id = rpn.review_id "
                     "GROUP BY b.business_id "
                     "ORDER BY count(rpn.positive) DESC "
                     "LIMIT %s;" % (category_id, n))

    tup = ()
    for i in cu:
        tup += (i)

    return [("business_id", "numberOfreviews"), tup]


def traceUserInfuence(userId, depth):
    # Create a new connection
    con = connection()
    # Create a cursor on the connection
    cur = con.cursor()

    tu = ()
    tu += userId

    int1 = depth
    for i in range(int(int1)):
        k = 0
        while k < len(tu):
            cu = cur.execute('SELECT f.friend_id '
                             'FROM user u1, user u2, reviews r1, reviews r2, friends f '
                             'WHERE u1.user_id = "%s" and u1.user_id = f.user_id and u2.user_id = f.friend_id and '
                             'u1.user_id = r1.user_id and u2.user_id = r2.user_id and '
                             'r1.business_id = r2.business_id and r1.date < r2.date' % (tu(k)))
            k += 1
        for j in cu:
            tu += j

    return [("user_id",), tu]
