#!usr/bin/env python

"""
 @name  DBSide
 @info  The program developed to create communication Date base and MQTT broker.
        The message recieved by the MQTT class from the MQTT broker send to Data base.
 @ver   1.0
 @note
 @author Baba Mehdi, Mehdi; Walsken, Daniel; Voss, Carina
"""

import time
import sys
import sqlite3 # Database client

# MQTT Broker
import paho.mqtt.client as mqtt

# Logging
import logging
logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


def main():
   """
    @name  MyMQTTClass
    @info  The class developed to communicate to MQTT broker.
           The message recieved by the MQTT class from the MQTT broker send to Data base,
           it is carried out by putting recieved msg to a queue (queueDB)

    @input clientID: the client ID used to connect to MQTT Broker
           queueDB:  The queue used to send data recieved by the MyMQTTClass thread to DB class
   """
   class MyMQTTClass():

      def __del__(self):
         self.dbconn.close()

      def __init__(self, clientID):
         self.clientID = clientID

         self.brokerAddress = "broker"  	# Broker Address
         self.port = 1883                       # Broker Port
         self.subTopic = "VirtualProject"       # Topic
         self.entry_counter = 0
         self.DBPath = "/DB/data.db"
         self.dbconn = 0                    # Connection to the database
         self.brokerconn = False                 # Connection to broker

      def on_connect(self, userdata, obj, flags, rc):
         self.mqttClient.subscribe(self.subTopic, 0)
         print("Connected to broker")

      def on_disconnect(self, client, userdata, rc):
         print("Connection to MQTT broker terminated")

      """Quite a long method, but it makes sure to only write every prime once
      to the database and create the table from scratch, if the database gets
      changed from outside"""
      def on_message(self, userdata, obj, msg):
         if not self.dbconn:
            try:
               self.dbconn = sqlite3.connect(self.DBPath)
               self.c = self.dbconn.cursor()
               print("CONNECTED TO DB")
               self.c.execute('''CREATE TABLE primes (id numerical primary key, prime
                     numerical)''')
            except Exception as ex:
               print(ex, file=sys.stderr)

         self.entry_counter = self.entry_counter + 1
         strMsg = int(msg.payload)
         print(f"MQTT Message   topic:{msg.topic} , Payload: {strMsg}")
         try:
             self.c.execute("SELECT id from primes where prime=?",
                     (strMsg,))
         except Exception:
             self.c.execute("""CREATE TABLE primes (id numerical primary key, prime
                     numerical)""")
             self.entry_counter = 1
             self.c.execute('''INSERT INTO primes (id, prime) VALUES ({},
                     {}'''.format(self.entry_counter, strMsg))

         data = list(self.c.fetchall())
         if data == []:
             try:
                self.c.execute('''INSERT INTO primes (id, prime)
                      VALUES ({}, {})'''.format(self.entry_counter , strMsg))
                self.dbconn.commit()
             except Exception as ex:
                print(ex)
                self.c.execute('''CREATE TABLE primes (id numerical primary key, prime
                      numerical)''')
                self.c.execute('''INSERT INTO primes (id, prime)
                      VALUES ({}, {})'''.format(self.entry_counter , strMsg))
                self.dbconn.commit()
                self.entry_counter = 1

      def on_subscribe(self, userdata, obj, mid, granted_qos):
         print("Subscribed: " + str(mid) + " " + str(granted_qos))

      def on_log(self, userdata, obj, level, string):
         print(string)

      def run(self):
         self.mqttClient = mqtt.Client(self.clientID, clean_session=False)
         self.mqttClient.on_message = self.on_message
         self.mqttClient.on_connect = self.on_connect
         self.mqttClient.on_disconnect = self.on_disconnect
         self.mqttClient.on_subscribe = self.on_subscribe
         self.mqttClient.on_log = self.on_log
         try:
             self.mqttClient.connect(self.brokerAddress, self.port, 60)
             self.brokerconn = True
             print ("Connected to MQTT broker!")
         except:
             print ("Can not Connect to broker!")

         if self.brokerconn:
             self.mqttClient.subscribe(self.subTopic, 0)
             self.mqttClient.loop_forever()


   # Connect to MQTT Broker
   myMqtt = MyMQTTClass("DBClient")
   myMqtt.run()


if __name__ == "__main__":
    main()
