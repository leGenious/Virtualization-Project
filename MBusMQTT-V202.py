#!usr/bin/env python3

# Ver. 2.01
# It is a format of the code which is works fine. all the other versions of 
#    the code are modification of this version
# Apply the following changes:
# 1- When internet available, connected to broker

import sys
import Queue
import socket
import threading
import select
import time
import datetime

import logging
try:
    import httplib
except:
    import http.client as httplib

from functools import wraps

# ModBus
from pymodbus.server.sync import StartTcpServer,ModbusBaseRequestHandler
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

# MQTT Broker
import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


#
# In this program it is suuposed that PLC is a client and RPi is server.
# msg from PLC --> get by server --> QueueIn --> Publish
# msg from MQTT Broker --> QueueOut --> sent to client --> sent to PLC
# temp --> Request
# sensor/temp --> Response
#
# C --> COIL ; R --> REGISTER ; I --> INPUT ; O --> OUTPUT
#


def main():



   
   #
   # @name  DataStructure
   # @brief The class is data structure by which its instance refers to Coil/Reg/Input/Output
   #        in PLC, their types, address and value.
   #
   class DataStructure():

      _registry = []

      def __init__(self,memName,memType,memAddress,memValue=None):
         self._registry.append(self)
         self.memName = memName
         self.memType = memType
         self.memAddress = memAddress
         self.memValue = memValue
         

      def setMemValue (value):
         self.memValue = value


      def getMemValue():
         return self.memValue


      def getMemAddress():
         return self.memAddress

      def getMemType():
         return self.memType
        
       
   ################################################
   class MyMQTTClass(threading.Thread):

      def __init__(self, clientID,queueIn, queueOut):
         threading.Thread.__init__(self)
         self.running = 1
         self.clientID = clientID
         self.queueIn = queueIn
         self.queueOut = queueOut
         
         self.brokerAddress = "m14.cloudmqtt.com"  	# Broker Address
         self.port = 19498                         	# Broker Port
         self.username = "hietjmix"                     # Connection Username
         self.password = "phsGN50Jflk5"            	# Connection Password
         
         self.pubTopic = "sensor/temp"
         self.subTopic = "temp"
              
      def on_connect(self, mqttClient, obj, flags, rc):
         global flag_connected 
         flag_connected = 1
         if rc != 0:
            print("Connection Failed")
            flag_connected = 0
            
      
      def on_disconnect(client, userdata, rc):
         global flag_connected 
         flag_connected = 0

      
      def on_message(self, mqttClient, obj, msg):

         global flag_connected
         print("MQTT Message   topic:" + msg.topic + " , Payload:" + str(msg.payload))
         stsMsg = msg.payload.decode("utf-8", "ignore")
         if str(stsMsg) == "990200":
            if flag_connected == 1:
               StatusMqttMsg = "990201"  # R000 is added to comply with message format
               self.mqttClient.publish(self.pubTopic, StatusMqttMsg, qos=0)
         else:
            try:
               queueLock.acquire()
               print("MQTT, Put The Outdata")
               self.queueOut.put(str(msg.payload))
            except:
               print ("Error: MQTT, On_Message, Queue Lock Acquire")
            finally:
               queueLock.release()
               print("Release queueout")


      
      def on_publish(self, mqttClient, obj, mid):
         print("mid: " + str(mid))

      
      def on_subscribe(self, mqttClient, obj, mid, granted_qos):
         print("Subscribed: " + str(mid) + " " + str(granted_qos))

      
      def on_log(self, mqttClient, obj, level, string):
         print(string)

      
      def run(self):
         
         # Check if Intenet Connection is available
         internetConnection = 0
         url="www.google.com"
         timeout=5         

         self.mqttClient = mqtt.Client(self.clientID)
         self.mqttClient.on_message = self.on_message
         self.mqttClient.on_connect = self.on_connect
         self.mqttClient.on_publish = self.on_publish
         self.mqttClient.on_subscribe = self.on_subscribe
         #self.mqttClient.on_log = self.on_log
         
         self.mqttClient.username_pw_set(self.username,self.password)
         try:
             self.mqttClient.connect(self.brokerAddress, self.port, 60)
             print ("Connected to MQTT Broker!")
             StatusMqttMsg = "990201"  # R000 is added to comply with message format
             self.mqttClient.publish(self.pubTopic, StatusMqttMsg, qos=0)
         except:
             print ("Can not Connect to Broker!")
         
         self.mqttClient.subscribe(self.subTopic, 1)
         self.mqttClient.loop_start()

         while True:
            conn = httplib.HTTPConnection(url, timeout)
            try:
               conn.request("HEAD", "/")
               conn.close()
                  
               if internetConnection == 0:
                  internetConnection = 1         
                  try:
                     self.mqttClient.connect(self.brokerAddress, self.port, 60)
                     print ("Connected to MQTT Broker!")
                     statusMqttMsg = "990201"  # R000 is added to comply with message format
                     self.mqttClient.publish(self.pubTopic, statusMqttMsg, qos=0)
                  except:
                     print ("Can not Connect to Broker!")
             
                  self.mqttClient.subscribe(self.subTopic, 1)
                  self.mqttClient.loop_start()
            except:
               internetConnection = 0
               conn.close()
               print ("Internet is not Available! Try When Available")
            
            if internetConnection == 1:
               queueLock.acquire()
               if not self.queueIn.empty():
                  print("MQTT, Get The Indata")
                  msg=self.queueIn.get()
                  queueLock.release()
                  self.mqttClient.publish(self.pubTopic, msg, qos=0)
               else:
                  queueLock.release()
            time.sleep(2)
         #logging.debug('Stopping MQTT')

         with queueLock.acquire() as
            

   ####################################################
   class Modbus_Server(threading.Thread):

      def __init__(self,queueIn,queueOut,context):
         threading.Thread.__init__(self)
         self.running = 1
         
         self.queueIn = queueIn
         self.queueOut = queueOut
         self.context = context
                  
         self.funcCodedigit = 2
         self.countdigit = 2
         self.regAddressdigit = 2
         self.regValuesdigit = 5
         
      """
       This section of the class are responsible to make modbus request based on
       the fucntion code in the recived message from user via MQTT cloud, The waits
       for the response from the PLC/PC (Modbus Response) in case of Reading
       Coil/Register and then sends the Response from PLC/PC to the user via
       MQTT cloud (By Publishing in MQTT Class in run function), and in the
       case of write on Coil/Register print the response if it is OK or and error accured.
      """
		
      def run(self):
         
         print(">>> Starting Modbus Server ... ")
         slaveID = 1

         while True:
                    
            queueLock.acquire()
            if not self.queueOut.empty():
               # Get the msg sent by MQTT
               print ("QueueOut is not Empty")
               msg=str(self.queueOut.get())
               queueLock.release()
               print("Msg From MQTT Class: " + msg)
               
               if (len(msg) < self.funcCodedigit+self.countdigit+self.regAddressdigit):
                  print ("Error in number of received data!!")
                  
               else:

                  # Extarct different parts of the msg
                  funCode = msg[0:self.funcCodedigit]
                  count = msg[self.funcCodedigit:self.funcCodedigit+self.countdigit]
                  regAdd = msg[self.funcCodedigit+self.countdigit:self.funcCodedigit+self.countdigit+self.regAddressdigit]
                
  
                  # If the arbitary process is READING     
                  if ((funCode == "1".zfill(self.funcCodedigit)) | (funCode == "2".zfill(self.funcCodedigit)) \
                  | (funCode == "3".zfill(self.funcCodedigit)) | (funCode == "4".zfill(self.funcCodedigit))):
                     print ("The Massage : ", funCode , count , regAdd)
                     # Values given by PLC are list of Integer
                     values = self.context[slaveID].getValues(int(funCode.lstrip('0')),int(regAdd.lstrip('0')),int(count.lstrip('0')))

                     print ("Values : " , values)
                     if (len(values) > 0):
                        response = str(funCode) + str(count) + str(regAdd) + ''.join(str(x).zfill(self.regValuesdigit) for x in values) #Convert list to str

                     queueLock.acquire()
                     print("ModBus Server, Put Response in QueueIn")
                     self.queueIn.put(str(response))
                     queueLock.release()
                  
                  
                  # If the arbitary process is WRITING
                  elif ((funCode == "5".zfill(self.funcCodedigit)) | (funCode == "15".zfill(self.funcCodedigit)) \
                  | (funCode == "6".zfill(self.funcCodedigit)) | (funCode == "16".zfill(self.funcCodedigit))):
                     if (len(msg) < (int(count) * self.regValuesdigit + self.funcCodedigit+self.countdigit+self.regAddressdigit)):
                        print ("Error in number of data")
                     else:
                        values = []
                        for i in range(int(count)):
                           values.append(msg[self.funcCodedigit+self.countdigit+self.regAddressdigit+i*self.regValuesdigit:
                           self.funcCodedigit+self.countdigit+self.regAddressdigit+(i+1)*self.regValuesdigit])
                           
                        print ("The Massage : ", funCode , count , regAdd , values)
                        
                        # Convert items to integer, because PLC accepts only list of integer
                        try:
                           values = map(int,values)
                        except:
                           print ("Error in number of data")
                           
                        # all the items in the context.setValues are Integer or list of Integer
                        self.context[slaveID].setValues(int(funCode.lstrip('0')),int(regAdd.lstrip('0')),values)
                        print ("Write: " , values)
                        time.sleep(2)
                  
                        ret_values = []
                     
                        # Acknowledgement of updating the register/coil
                        ret_values = self.context[slaveID].getValues(int(funCode.lstrip('0')),int(regAdd.lstrip('0')),int(count.lstrip('0')))
                        print ("Values : " , ret_values)
                        if (len(values) > 0):
                           response = str(funCode) + str(count) + str(regAdd) + ''.join(str(x).zfill(self.regValuesdigit) for x in ret_values) #Convert list to str to append it to string sent to broker
                           print("Response: " + response)
                        queueLock.acquire()
                        print("ModBus Server, Put Response in QueueIn")
                        self.queueIn.put(str(response))
                        queueLock.release()
                  
            else:
                queueLock.release()
            time.sleep(5)
                  
            
      def kill(self):
         self.running = 0
 
 #########################################
   class connectionStatus():
      """ 
      This class uses interceptor to watch setup and finish functions in ModbusBaseRequestHandler
      class in sync.py in order to notify the user when a connection in modbus server side 
      (RPi as server and PLC as client) establishes and destroys
      """
      def __init__(self,connEstCode):
         self.connEstCode = connEstCode
   
      def connStatus(self):
         
         queueLock.acquire()
         print("ModBus Alarming Code, Put Code in QueueIn")
         queueIn.put(str(self.connEstCode))
         queueLock.release()
      
   
      def interceptor(self,func):
          
          @wraps(func)
          def wrapper(*args, **kwargs):
              result = func(*args, **kwargs)
              self.connStatus()
              return result

          return wrapper
   
   
   
   queueLock = threading.Lock()
   queueIn = Queue.Queue(10)
   queueOut = Queue.Queue(10)
 
 
   myMqtt = MyMQTTClass("Client1",queueIn, queueOut)
   myMqtt.start()
   time.sleep(3) # Wait for Establishing Connection to Broker

   
   # Set up Modbus library and data block stores data from appointed address 
   # in PLC. It is premised 100 array which equals zero at beginning ([0]*100)
   identity = ModbusDeviceIdentification()
   identity.VendorName  = 'Pymodbus'
   identity.ProductCode = 'PM'
   identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
   identity.ProductName = 'Pymodbus Server'
   identity.ModelName   = 'Pymodbus Server'
   identity.MajorMinorRevision = '1.0'

   store = ModbusSlaveContext(
      di = ModbusSequentialDataBlock(0, [0]*100),
      co = ModbusSequentialDataBlock(0, [0]*100),
      hr = ModbusSequentialDataBlock(0, [0]*100),
      ir = ModbusSequentialDataBlock(0, [0]*100))
   context = ModbusServerContext(slaves=store, single=True)
   
   print(">>> Running as a Server ... ")
   myServer = Modbus_Server(queueIn, queueOut, context)
   myServer.start()
   
   
   # The data frame created here includes alarm message (code 99), 
   # related to connection ststus (01) and connection status (00: loss, 01 establish) 
   connEstCode = "990101"
   connLossCode = "990100"
   connEst = connectionStatus(connEstCode) 
   connLoss = connectionStatus(connLossCode) 
   ModbusBaseRequestHandler.setup = connEst.interceptor(ModbusBaseRequestHandler.setup)
   ModbusBaseRequestHandler.finish = connLoss.interceptor(ModbusBaseRequestHandler.finish)



   Server_IP = "0.0.0.0"
   Server_Port = 502 
   StartTcpServer(context, identity=identity, address=(Server_IP, Server_Port))
   
   
if __name__ == "__main__":
    main()
