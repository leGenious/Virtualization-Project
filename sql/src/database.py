import sqlite3
import pprint
import sys
import paho.mqtt.client as mqtt

''' some other function'''
def make_database():
    try:
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE primes
                        (id numerical, prime numerical)''')
    except (e):
        print(e)
    return conn

''' some function'''
def print_to_db(conn, index, prime):
    c = conn.cursor()
    c.execute('''INSERT INTO primes (id, prime)
           VALUES ({}, {})'''.format(index, prime))

def main():
    db = make_database()


if __name__ == '__main__':
	main()
