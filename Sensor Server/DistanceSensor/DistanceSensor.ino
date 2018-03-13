/*
  Distance sensor
  recieves six sensor values using software serial.
  

  The circuit:
Six maxbotic distance sensors are connected to software sirial ports . 

the six software serial ports are held in an array so that the can be itrated 
  
 
  created  oct 2017
 
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
// the purpose of this function is to read the sensor data and added to the allsensorData varible.
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

// the purose of this function is to return true if sensor connected
boolean isSensorConnected(int index)
{
  // the port will return high if sensor connected.
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

