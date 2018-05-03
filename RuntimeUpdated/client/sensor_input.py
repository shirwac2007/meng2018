""" Sensor Input Serial handler"""

import sys
import serial
import time
import serial.tools.list_ports
import threading
import os
from Queue import Queue
import traceback

port = "COM6"
samples_to_average = 3

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
           time.sleep(2)

    """ 
    def latest_data(self):
        if self.msgQ.qsize() == 0:
            print "No sensor messages received"
            return None
        else:
            msg = None
            while self.msgQ.qsize() > 0:
                msg = self.msgQ.get()
                print "queue=", msg
            sensor_data = self.msg_to_floats(msg, "H", 9)
            return sensor_data
    """
    def latest_data(self):
        print  "q size ==", self.msgQ.qsize()
        while self.msgQ.qsize() > samples_to_average:
            m = self.msgQ.get() # FIFO, ignore all but the last three messages
            print "ignoring extra data", m
        if self.msgQ.qsize() < samples_to_average:
            print "Waiting for", samples_to_average, "messages from sensor server"
            while self.msgQ.qsize() < samples_to_average:
                # print "waiting..."
                time.sleep(.2)
                pass
        # here if we have three messages
        average = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for i in xrange(samples_to_average):
            msg = self.msgQ.get()
            print "queue=", msg
            sensor_data = self.msg_to_floats(msg, "H", 9)
            for idx, val in enumerate(sensor_data):
               average[idx] = average[idx] + sensor_data[idx]
        for idx, val in enumerate(average):
            average[idx] = average[idx] / samples_to_average
        return average

    def msg_to_floats(self, message, header, nbr_fields):
        if message != None and header != None:
            try:
                msg = message.rstrip()
                fields = msg.split(",")
                if fields[0] == header:
                    data = [float(f) for f in list(fields[1:nbr_fields+1])]
                    # print msg[0], ['%.2f' % elem for elem in data]
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
                    #  print "q in=", result
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
    sensors = SensorInput()
    while True:
         print "average:", sensors.latest_data(), "/n"
         time.sleep(.1)
