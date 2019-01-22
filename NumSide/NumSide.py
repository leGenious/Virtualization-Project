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
 @author Baba Mehdi, Mehdi; Walsken, Daniel; Voss, Carina
"""

import time
import math
import paho.mqtt.client as mqtt # MQTT Broker

import logging                  # Logging
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

         self.brokerAddress = "broker"      # Broker Address
         self.port = 1883                   # Broker Port
         self.pubTopic = "VirtualProject"   # Topic
         self.maxprime = 10000000            # Maximum Prime to calculate

      def on_connect(self, userdata, obj, flags, rc):
         print("Connected")

      def on_disconnect(self,client, userdata, rc):
         print("Connection to MQTT brocker terminated")

      def on_publish(self, userdata, obj, mid):
         print("mid: " + str(mid))

      def on_log(self, userdata, obj, level, string):
         print(string)

      """
      @name run
      @info The run method of MyMQTTClass. It connects to the (remote) broker
      under the address self.brokerAdress on port self.port and starts
      generating prime numbers up to self.maxprime using the sieve of
      erathostenes. Then it publishes them on the broker one at a time, with a
      delay of 500 ms between each publish, to make it visually more appealing
      """
      def run(self):
         self.mqttClient = mqtt.Client(self.clientID)
         self.mqttClient.on_connect = self.on_connect
         self.mqttClient.on_disconnect = self.on_disconnect
         self.mqttClient.on_publish = self.on_publish
         self.mqttClient.on_log = self.on_log

         try:
            self.mqttClient.connect(self.brokerAddress, self.port, 60)
            print ("Connected to MQTT Broker!")
         except:
            print ("Can not Connect to Broker!")

         mark = [1 if i>=2 else 0 for i in range(self.maxprime)]

         for i in range(2, int(math.sqrt(len(mark)))):
            for j in range(i*i, len(mark), i):
               mark[j] = 0

         for i in range(2, len(mark)):
            if mark[i]:
               print(f"Publishing prime {i}")
               self.mqttClient.publish(self.pubTopic, str(i), qos = 0)
               time.sleep(0.5)

         logging.debug('Stopping MQTT')

   # Connect to MQTT Broker
   myMqtt = MyMQTTClass("NumClient")
   myMqtt.run()
   time.sleep(2) # Wait for Establishing Connection to Broker

if __name__ == "__main__":
    main()
