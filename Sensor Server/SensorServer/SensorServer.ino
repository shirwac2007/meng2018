// ChairMonitorMaster
#include <SoftwareSerial.h>
#include <math.h>
#include <Wire.h>

SoftwareSerial megaIn(10, 11); // RX, TX

unsigned long messageCounter = 0; // number of messages sent
float roll, pitch, heading ;
String  sensorData = "";
int distances[6]; //global array holding six distance sensor readings

void setup() {

  //initialize Imu here
  // initialize serial communication
  Serial.begin(9600); // initialize Serial
  megaIn.begin(9600);
  jyBegin();


  // set the data rate for the SoftwareSerial port
  megaIn.begin(9600);
  megaIn.flush();
  delay(1000);
}

void loop() {
  float roll, pitch, heading;
  // check if it's time to read data and update the filter

  getAngles( roll, pitch, heading);
  String sensorData = "";
  sensorData = MagaData();
  String AngleData = "";

  AngleData += "Angles  ";

  AngleData += String(roll);
  AngleData += ", ";
  AngleData += String(pitch);
  AngleData += ", ";
  AngleData += String(heading);
  AngleData += ",";

  Serial.println( sensorData + AngleData);
  messageCounter++;
  delay(1000);
}


// wait till data is availabe and return distance data string
String MagaData()
{
  sensorData = "";
  while (true)
  {
    char c = readChar();

    if ( c == 'H')
    {
      while (true)
      {
        char received = readChar();
        if (received == '\n')
        {
          break;
        }
        else if (received != 0)
        {
          sensorData += received ;
        }
      }
      return (sensorData );
    }
  }
}

//it returns char if availble else zero 
char readChar()
{
  if ( megaIn.available() > 0) {
    return megaIn.read();
  }
  return 0; 
}

void getAngles(float & roll, float & pitch, float & heading)
{
  static short data[4];
  jyGetAngle(data);
  roll = (float)data[0] / 32768 * 180;
  pitch = (float)data[1] / 32768 * 180;
  heading = (float)data[2] / 32768 * 180;


}



float convertRawAcceleration(int aRaw) {
  // since we are using 2G range
  // -2g maps to a raw value of -32768
  // +2g maps to a raw value of 32767
  float a = (aRaw * 2.0) / 32768.0;
  return a;
}
float convertRawGyro(int gRaw) {
  // since we are using 250 degrees/seconds range
  // -250 maps to a raw value of -32768
  // +250 maps to a raw value of 32767
  float g = (gRaw * 250.0) / 32768.0;
  return g;
}




