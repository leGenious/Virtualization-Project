# A minimal SQLite shell for experiments

import sqlite3
import pprint

con = sqlite3.connect("data.db")
con.isolation_level = None
cur = con.cursor()

buff = ""

print("Enter your SQL commands to execute in sqlite3.")
print("Enter a blank line to exit.")

while True:
    line = input()
    if line == "":
        break
    buff += line
    #if sqlite3.complete_statement(buff):
    try:
        print("Executed " + buff)
        buff = buff.strip()
        cur.execute(buff)

        if buff.lstrip().upper().startswith("SELECT"):
            pprint.pprint(cur.fetchall())
    except sqlite3.Error as e:
        print("An error occurred:", e.args[0])
    buff = ""

con.close()
