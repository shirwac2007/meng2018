/*
  Software serial multple serial test

  Receives from the two software serial ports,
  sends to the hardware serial port.

  In order to listen on a software port, you call port.listen().
  When using two software serial ports, you have to switch ports
  by listen()ing on each one in turn. Pick a logical time to switch
  ports, like the end of an expected transmission, or when the
  buffer is empty. This example switches ports when there is nothing
  more to read from a port

  The circuit:
  Two devices which communicate serially are needed.
   First serial device's TX attached to digital pin 10(RX), RX to pin 11(TX)
   Second serial device's TX attached to digital pin 8(RX), RX to pin 9(TX)

  Note:
  Not all pins on the Mega and Mega 2560 support change interrupts,
  so only the following can be used for RX:
  10, 11, 12, 13, 50, 51, 52, 53, 62, 63, 64, 65, 66, 67, 68, 69

  Not all pins on the Leonardo support change interrupts,
  so only the following can be used for RX:
  8, 9, 10, 11, 14 (MISO), 15 (SCK), 16 (MOSI).

  created 18 Apr. 2011
  modified 19 March 2016
  by Tom Igoe
  based on Mikal Hart's twoPortRXExample

  This example code is in the public domain.
  first change of gihub
*/

#include <SoftwareSerial.h>


SoftwareSerial outport(51, 50);
SoftwareSerial port1(62, 14);
SoftwareSerial port2(63, 15);
SoftwareSerial port3(64, 16);
SoftwareSerial port4(65, 17);
SoftwareSerial port5(66, 18);
SoftwareSerial port6(67, 19);

const int NUMBER_OF_PORTS = 6;
const int FIRST_CTRL_PORT = 14;
String allsensorData = "";

SoftwareSerial port[NUMBER_OF_PORTS] = {port1, port2, port3, port4, port5, port6};

void setup() {

  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  outport.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  // Start each software serial port
  for (int i = 0; i < NUMBER_OF_PORTS; i++) {
    port[i].begin(9600);
  }
  Serial.println("ready");
}

void loop() {
  allsensorData = "";
  allsensorData += "H ";
  for (int i = 0; i < NUMBER_OF_PORTS; i++) {
    readSensor(i);
  }
  allsensorData += "\n";
  {
    outport.println(allsensorData);
    Serial.println(allsensorData);
    outport.flush();
  } delay(1000);
  // Serial.println();
}

void readSensor(int index)
{
  int nbrChars = 0; // how many digits read from sensor
  char c;
  //allsensorData += String(index);
  //  allsensorData +=" = ";

  // we can read the ctrl port to see if sensor is connected
  pinMode(FIRST_CTRL_PORT + index, INPUT);
  if (isSensorConnected(index)) {
    // when you want to listen on a port, explicitly select it:
    port[index].listen();
    while ((c = readChar(index)) != 0 )
    {
      if ( c == 'R')
      {
        while ( nbrChars < 4)
        {
          c = readChar(index);
          if ( c == 0) {
            allsensorData = allsensorData + "0,";
            return;
          }
          allsensorData += String(c);
          nbrChars++;
        }
        allsensorData = allsensorData + ",";
        return;
      }
    }
   
  }
  // here only if sensor not connected
 allsensorData = allsensorData + "0,";
 
}

char readChar(int index)
{
  while (isSensorConnected(index))
  {
    if ( port[index].available() > 0) {
      return port[index].read();
    }
  }
  return 0; // no sensor connected
}

boolean isSensorConnected(int index)
{
  return digitalRead(FIRST_CTRL_PORT + index) == HIGH;
}

void test()
{
  for (int i = 0; i < NUMBER_OF_PORTS; i++) {
    if (digitalRead(FIRST_CTRL_PORT + i) == HIGH)
      Serial.print("H");
    else
      Serial.print("L");
  }
  Serial.println();
  delay(100);
}

