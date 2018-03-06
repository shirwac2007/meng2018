"""
  Monitor for Chair testing

  sends test xyzrpy messages to move chair and compares with sensor values
  receives actuator UDP messages on port 10010
  xyz values are mm, angles are degrees
"""

import sys
import time
import traceback
import math
from sensor_input import SensorInput
from controller_input import ControllerInput

settling_interval = .1 # seconds between command and measurement

"""
  data from sensors is: 6 lengths in mm followed by roll pitch yaw in degrees
  data from controler is: xyzrpy commands in mm and radians, muscle lengths in mm  
  compare_sequence  defines the controller data field index to be compared to the sensor fields
  change this if the sensor data order is changed
"""
compare_sequence = [6,7,8,9,10,11,3,4,5] 

class InputInterface(object):
    USE_GUI = False  # set True if using tkInter
    
    def __init__(self):
        #  set True if input range is -1 to +1
        self.is_normalized = False
        self.expect_degrees = True # convert to radians if True
        if self.is_normalized:
            print 'Platform Input uses normalized parameters'
        else:
            print 'Platform Input uses realworld parameters'

        self.levels = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # command values sent to the chair
        self.angles = [0,4,8,12,16,20,0,-4,-8,-12,-16,-20]  # range of angles (roll, pitch, yaw) to be measured
        self.translations = [0,2,4,6,8,10,0,-2,-4,-6,-8,-10] #range of translation (x,y,z) movements
        self.sensors = SensorInput()
        self.controller = ControllerInput()

    def quit(self):
        self.command("quit")

    def command(self, cmd):
        if self.cmd_func is not None:
            print "Requesting command:", cmd
            self.cmd_func(cmd)

    def chair_status_changed(self, chair_status):
        print(chair_status[0])
    
    def intensity_status_changed(self, intensity):
       self.intensity_status_Label.config(text=intensity[0], fg=intensity[1])

    def begin(self, cmd_func, move_func, limits):
        self.cmd_func = cmd_func
        self.move_func = move_func
        self.limits = limits  # note limits are in mm and radians
        self.cmd_func("enable")  #  enable the platform
        self.state = 0 # states are translations and rotations
        self.sequence = 0 # sequences are: neutral, 5 steps up, neutral, 5 steps down
        self.move_func(self.levels)  # move to neutral
        self.outfile = open("errors.csv","w")
        self.next_reading_time = time.time() + settling_interval


    def fin(self):
        # client exit code goes here
        self.outfile.close()
        
    def get_current_pos(self):
        return self.levels

    def service(self):
        if time.time() > self.next_reading_time:  # two seconds between chair movements
            self.next_reading_time = time.time() + settling_interval
            self.process_data()
            self.move_platform()

    def process_data(self):
        sensor_data = self.sensors.latest_data()
        controller_data = self.controller.latest_data()
        if sensor_data and controller_data:
            # print sensor_data, " : ", controller_data,
            expected_values = []
            error_values = []
            for idx, val in enumerate(compare_sequence):
                 idx_of_ctrl_data = compare_sequence[idx] # the ith index of sensor data is compared to this index into control data
                 expected_values.append(controller_data[ idx_of_ctrl_data])
                 # sensor rpy in sent as degrees, but controller uses radians
                 if idx >= 6: # angles follows the six lengths, convert to degrees
                    expected_values[idx] = math.degrees( expected_values[idx])
                 error_values.append(expected_values[idx] - sensor_data[idx])
            outstring = ','.join([str(i) for i in error_values])
            print outstring
            if self.outfile:
                self.outfile.write(str(outstring)+"\n")
        else:
           if sensor_data == None:
               print "NO SENSOR DATA"
           if controller_data == None:
               print "NO CONTROLLER DATA"


    def move_platform(self):
        # move platform to position for the current state and sequence indices 
        self.levels = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # reset all fields
        if self.state < 3:
           self.levels[self.state] = self.translations[self.sequence]
           self.sequence += 1
           if self.sequence >= len(self.translations):
               self.state = self.state + 1
               self.sequence = 0
        else:
           self.levels[self.state] = self.angles[self.sequence]
           self.sequence += 1
           if self.sequence >= len(self.angles):
               self.state = self.state + 1
               self.sequence = 0
        if  self.state > 5:
            print "finished all measurements"
            exit()
        else:
            self.move_func(self.levels)
            send_dummy_controller_msg(self.controller, self.levels)  # only for testing
            print "state=", self.state, " sequence=", self.sequence

def send_dummy_controller_msg(controller, levels):
    xyzrpy = ','.join([str(i) for i in levels])
    lengths = ",700,710,720,730,740,750\n"
    controller.send_test_message("monitor," + xyzrpy + lengths) 
    
def cmd_func(cmd):  # command handler function called from Platform input
    if cmd == "enable":
        print "Received command to enable platform"
    elif cmd == "disable":
        print "Received command to disable platform"

def move_func(request):  # move handler to position platform as requested by Platform input
    print "Received request to move:", request

def main():
    client = InputInterface()
    previous = time.time()
    client.begin(cmd_func, move_func, [])
    print "starting main service loop"
    while True:
        if(time.time() - previous >= .05):
            client.service()

if __name__ == "__main__":
    main()
    client.fin()
