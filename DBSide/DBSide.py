#!usr/bin/env python

"""
 @name  DBSide
 @info  The program developed to create communication Date base and MQTT broker.
        The message recieved by the MQTT class from the MQTT broker send to Data base.
 @ver   1.0
 @note
"""

import sys
import time
import requests
import sqlite3

# MQTT Broker
import paho.mqtt.client as mqtt

# Logging
import logging
logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


def main():


   ####################################################################################
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
         self.conn.close()

      def __init__(self, clientID):
         self.clientID = clientID

         self.brokerAddress = "m16.cloudmqtt.com"  	# Broker Address
         self.port = 19824                         	# Broker Port
         self.username = "jjrjqtif"                 # Connection Username
         self.password = "7maZnKmglGfG"            	# Connection Password
         self.subTopic = "VirtualProject"
         self.entry_counter = 0
         self.DBPath = "/DB/data.db"
         self.conn = 0
#         try:
#            self.conn = sqlite3.connect('data.db')
#            self.c = self.conn.cursor()
#            self.c.execute('''CREATE TABLE primes
#                            (id numerical, prime text)''')
#         except Exception as ex:
#            print(ex)

      def on_connect(self, userdata, obj, flags, rc):
         print("Connection Failed")

      def on_disconnect(self, client, userdata, rc):
         print("Connection to MQTT brocker terminated")

      def on_message(self, userdata, obj, msg):
         if (not self.conn):
            try:
               self.conn = sqlite3.connect(self.DBPath)
               self.c = self.conn.cursor()
               self.c.execute('''CREATE TABLE primes (id numerical, prime
                     text)''')
            except Exception as ex:
               print(ex)
         self.entry_counter = self.entry_counter + 1
         strMsg = msg.payload.decode("utf-8", "ignore")
         print("MQTT Message   topic:" + msg.topic + " , Payload:" + strMsg)
         try:
            self.c.execute('''INSERT INTO primes (id, prime)
                  VALUES ({}, "{}")'''.format(self.entry_counter , strMsg))
            self.conn.commit()
         except sqlite3.OperationalError:
            self.c.execute('''CREATE TABLE primes (id numerical, prime
                  text)''')
            self.entry_counter = 0

      def on_subscribe(self, userdata, obj, mid, granted_qos):
         print("Subscribed: " + str(mid) + " " + str(granted_qos))


      def on_log(self, userdata, obj, level, string):
         print(string)


      def run(self):

         # Check if Intenet Connection is available
         internetConnection = 0
         url='http://www.google.com/'
         timeout=5

         self.mqttClient = mqtt.Client(self.clientID, clean_session=False)
         self.mqttClient.on_message = self.on_message
         self.mqttClient.on_connect = self.on_connect
         self.mqttClient.on_disconnect = self.on_disconnect
         self.mqttClient.on_subscribe = self.on_subscribe
         self.mqttClient.on_log = self.on_log

         self.mqttClient.username_pw_set(self.username,self.password)
         try:
             self.mqttClient.connect(self.brokerAddress, self.port, 60)
             print ("Connected to MQTT Broker!")

         except:
             print ("Can not Connect to Broker!")

         self.mqttClient.subscribe(self.subTopic, 0)
         self.mqttClient.loop_start()

         while True:
            try:
               _ = requests.get(url, timeout=timeout)
               print ("Internet is available!")

               if internetConnection == 0:

                  try:
                     self.mqttClient.connect(self.brokerAddress, self.port, 60)
                     print ("Connected to MQTT Broker!")
                     internetConnection = 1
                  except:
                     print ("Can not Connect to Broker!")

                  self.mqttClient.loop_start()
                  self.mqttClient.subscribe(self.subTopic, 0)
            except requests.ConnectionError:
               internetConnection = 0
               print ("Internet is not Available! Try When Available")


            time.sleep(20)
         #logging.debug('Stopping MQTT')

 ############################################################################################


   # Connect to MQTT Broker
   myMqtt = MyMQTTClass("Client2")
   myMqtt.run()


if __name__ == "__main__":
    main()
