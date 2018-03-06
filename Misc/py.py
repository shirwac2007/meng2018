import serial # initaliz serial communication 
arduinodata = serial.Serial('COM6', 9600, timeout=.1) # COM5 is port number to which we have attached arduino uno
while True: # untill we receive data from serial
	receiveddata = arduinodata.readline()[:-2] #the -2 is used to remove \n from data received
	if receiveddata:# if there is data then print it
		print receiveddata
