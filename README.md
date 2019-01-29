# Virtualization-Project

## Introduction

This is an example project for the course "Virtualization 1" at BUW (Germany) 

## Goal

The Task is to make a virtual environment and run a mqtt broker, a database and a prime number generator in different virtual environments.
This is achieved using docker.

## The database

The  database uses python to open and write to a sqlite3 database.
First it will try to connect to the broker. If it is not running, it will not try again, it will just give an error. 
If it can connect it will subscribe to a Topic and write every message from the broker to the database in the following form:
+ (numerical primary id; int prime)

The following features make it less prone to crashes:
+ If the connection terminates, it will resubscribe on reconnect.
+ It will recreate the table if something terrible happens to the database (e.g. echo "" > data.db). 

## The Prime Generator

The numerical side of the project is a sieve of erastothernes.
It will generate a list of prime numbers and publish them (with a short delay) on the Topic.

## print.py & others

In the directory of the database there are a few scripts to visualize the data getting written to the db.
The print.py script will print the whole database and loop forever, printing additions to the database.
The min_shell.py script offers a minimal shell to the database, where you can run commands to get data from the table.
It is by large copied from the sqlite3 tutorial page.
The printDB.py script is very minimal and inefficient, since it prints the whole database every second to the screen.
