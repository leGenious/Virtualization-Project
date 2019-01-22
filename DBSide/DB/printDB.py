import sqlite3
import time

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

def main():
    with connect("data.db") as conn:
        data = read_data(conn)
        time.sleep(1)
        while True:
            if read_data != data:
                time.sleep(5)
                data = read_data(conn)
                for i in read_data(conn):
                    print(i[1])

if __name__ == "__main__":
    main()
