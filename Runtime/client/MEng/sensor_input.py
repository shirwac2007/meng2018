""" Sensor Input Serial handler"""

import sys
import serial
import time
import serial.tools.list_ports
import threading
import os
from Queue import Queue
import traceback

port = "COM31"

class SensorInput(object):

    def __init__(self ):
        self.msgQ = Queue()
        self.ser = None
        self.ser_buffer = ""
        self.baud_rate = 9600
        self.timeout_period = 2
        self.is_connected = False
        if self._connect(port):
            print "Opened connection on",  port
            t = threading.Thread(target=self.rx_thread, args=(self.ser, self.msgQ,))
            t.daemon = True
            t.start()
        else:
           print "Can't open Serial port:", port
           exit()



    def latest_data(self):
        if self.msgQ.qsize() == 0:
            print "No sensor messages received"
            return None
        else:
            msg = None
            while self.msgQ.qsize() > 0:
                msg = self.msgQ.get()
            sensor_data = self.msg_to_floats(msg, "H", 9)
            return sensor_data

    def msg_to_floats(self, message, header, nbr_fields):
        if message != None and header != None:
            try:
                msg = message.rstrip()
                fields = msg.split(",")
                if fields[0] == header:
                    data = [float(f) for f in list(fields[1:nbr_fields+1])]
                    #  print msg[0], ['%.2f' % elem for elem in data]
                    return data
            except:
                #  print error if input not a string or cannot be converted into valid request
                e = sys.exc_info()[0]
                s = traceback.format_exc()
                print e, s
        return None

    def rx_thread(self, ser, RxQ):
        self.RxQ = RxQ
        self.ser = ser
        while True:
            #  wait forever for data to forward to client
            try:
                result = self.ser.readline()
                if len(result) > 0:
                    self.RxQ.put(result)
            except:
                print "serial error, is Sensor Server Connected?"
                self.RxQ.put("Reconnect Remote Control")

    def _connect(self, portName):
        # Private method try and connect to the given portName.

        self.connected = False
        self.ser = None
        result = ""
        try:
            self.ser = serial.Serial(portName, self.baud_rate)
            self.ser.timeout = self.timeout_period
            #self.ser.setDTR(False)  
            if not self.ser.isOpen():
                print "Connection failed:", portName, "has already been opened by another process"
                self.ser = None
                return False
            else:
              self.ser.flush()
              return True
        except:
            self.ser = None
            pass
        return False

if __name__ == "__main__": 
    sensors = SensorInput(actions)
    while True:
         sensors.service()
         time.sleep(.1)
