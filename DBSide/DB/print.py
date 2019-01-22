import sqlite3
import time

def main():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    data = []
    ld = 0
    while True:
        newdata = list(cur.execute("select * from primes"))
        ln = len(newdata)
        if ln != ld:
            for row in range(ld, ln):
                print(str(newdata[row][0]) + "st prime: " + str(newdata[row][1]))
            ld = ln
        time.sleep(5)

if __name__ == "__main__":
    main()
