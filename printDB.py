import sqlite3

def read_data(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM primes")
    return c.fetchall()

def connect(dbpath):
    try:
        conn = sqlite3.connect(dbpath)
        return conn
    except Exception as e:
        print(e)

def write_something(conn, sth):
    c = conn.cursor()
    c.execute("""INSERT INTO primes (id, prime) VALUES ({},
            "{}")""".format(sth[0], sth[1]))
    conn.commit()

with connect("data.db") as conn:
    for i in read_data(conn):
        print(i)

