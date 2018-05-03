""" Controller Monitor message handler"""

import sys
import socket
import time
import threading
import os
from Queue import Queue
import traceback

PORT = 10010  # UDP port for messages from controller messages to monitor

class ControllerInput(object):

    def __init__(self):
        self.msgQ = Queue()
        print "opening socket on", PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("localhost", PORT))
        t = threading.Thread(target=self.listener_thread, args= (self.sock, self.msgQ,))
        t.daemon = True
        t.start()
        
    def latest_data(self):
        if self.msgQ.qsize() == 0:
            print "No controller messages received"
            return None
        else:
            msg = None
            while self.msgQ.qsize() > 0:
                msg = self.msgQ.get()
            controller_data = self.msg_to_floats(msg, "monitor", 12)
            return controller_data

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
        
    def listener_thread(self, sock, controllerQ):
        """ This function receives UDP messages from the chair controller
            these begin with "monitor" and contain six xyzrpy values and six actuator lengths
        """
        try:
            self.MAX_MSG_LEN = 120

        except:
            e = sys.exc_info()[0]
            s = traceback.format_exc()
            print "thread init err", e, s
        while True:
            try:
                msg = sock.recv(self.MAX_MSG_LEN)
                if msg is not None:
                    # print msg 
                    if msg.find("monitor") == 0:
                        controllerQ.put(msg)
            except:
                e = sys.exc_info()[0]
                s = traceback.format_exc()
                print "listener err", e, s

    def send_test_message(self, msg):
       self.sock.sendto(msg,("localhost", PORT))
