#!usr/bin/env python

"""
 @name  project
 @info  The program developed to communicate with XBee modules and MQTT broker.
        It get the payload from XBee modules/MQTT Broker and send it to the other side
        (MQTT Broker/XBee modules respectively).
        each task is done by specific Thread.
        In the version source routing in xbee modules is applied.
 @ver   1.0
 @note
"""

import sys
import queue
import threading
import time
import requests
import math

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
           The message created by the < NumberClass > get from a queue (queueNum) and
           then publish it into MQTT broker.

    @input clientID: the client ID used to connect to MQTT Broker
           queueNum:  The queue used to send data from <NumberClass> thread to MyMQTTClass thread
   """
   class MyMQTTClass():

      def __init__(self, clientID):

         self.clientID = clientID

         self.brokerAddress = "m16.cloudmqtt.com"      # Broker Address
         self.port = 19824                             # Broker Port
         self.username = "jjrjqtif"                     # Connection Username
         self.password = "7maZnKmglGfG"                # Connection Password

         self.pubTopic = "VirtualProject"

      def on_connect(self, userdata, obj, flags, rc):
         print("Connected")


      def on_disconnect(self,client, userdata, rc):
         print("Connection to MQTT brocker terminated")


      def on_publish(self, userdata, obj, mid):
         print("mid: " + str(mid))


      def on_log(self, userdata, obj, level, string):
         print(string)


      def run(self):

         # Check if Intenet Connection is available
         internetConnection = 0
         url='http://www.google.com/'
         timeout=5

         self.mqttClient = mqtt.Client(self.clientID)
         self.mqttClient.on_connect = self.on_connect
         self.mqttClient.on_disconnect = self.on_disconnect
         self.mqttClient.on_publish = self.on_publish
         self.mqttClient.username_pw_set(self.username,self.password)
         self.mqttClient.on_log = self.on_log

         try:
            self.mqttClient.connect(self.brokerAddress, self.port, 60)
            print ("Connected to MQTT Broker!")
            internetConnection = 1
         except:
            print ("Can not Connect to Broker!")

         self.mqttClient.loop_start()

         while True:

            try:
               _ = requests.get(url, timeout=timeout)
               print ("Internet is available!")

               if not internetConnection:

                  try:
                     self.mqttClient.connect(self.brokerAddress, self.port, 60)
                     print ("Connected to MQTT Broker!")
                     internetConnection = 1

                  except:
                     print ("Can not Connect to Broker!")

                  self.mqttClient.loop_start()

            except requests.ConnectionError:
               internetConnection = 0
               print ("Internet is not Available! Try When Available")

            if internetConnection == 1:
               n = 1000


               mark = [1 for i in range(1000000)]

               for i in range(2, int(math.sqrt(len(mark)))):
                  for j in range(i*i, len(mark), i):
                     mark[j] = 0

               for i in range(len(mark)):
                  if mark[i]:
                     print(f"{i}")
                     self.mqttClient.publish(self.pubTopic, str(i), qos = 0)
                     time.sleep(0.5)

#               marked = list(range(n+1))
#
#               for i in range(len(marked)):
#                  marked[i] = False
#
#                  rootn = math.sqrt(n)
#                  rootn = int(rootn)
#
#                  for k in range(2,rootn+1):
#                      if marked[k] == False:
#                      #print(k)
#                          self.mqttClient.publish(self.pubTopic, str(k), qos = 0)
#                          time.sleep(2)
#                          for j in range(k*k, n+1, k):
#                              marked[j] = True
#
#
#                  for i in range(rootn+1, n-1):
#                      if not (marked[i]):
#                          print(i)
#                          self.mqttClient.publish(self.pubTopic, str(i), qos = 0)
#                          time.sleep(2)


            time.sleep(2)
         logging.debug('Stopping MQTT')






   # The event used to stop MQTT class until first discovery of XBee network finishes


   # Connect to MQTT Broker
   myMqtt = MyMQTTClass("NumClient")
   myMqtt.run()
   time.sleep(2) # Wait for Establishing Connection to Broker

if __name__ == "__main__":
    main()
