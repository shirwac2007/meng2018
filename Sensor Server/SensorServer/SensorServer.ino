// ChairMonitorMaster
#include <SoftwareSerial.h>
#include <math.h>
#include <Wire.h>

SoftwareSerial megaIn(10, 11); // RX, TX

unsigned long microsPerReading, microsPrevious;
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

  //intilizing the IMU and its variables


  // initialize variables to pace updates to correct rate
  microsPerReading = 1000000 / 4;
  microsPrevious = micros();
  //this means that it reads 25 times a second



  // set the data rate for the SoftwareSerial port
  megaIn.begin(9600);
  megaIn.flush();
  delay(1000);
}

void loop() {
  float roll, pitch, heading;
  // check if it's time to read data and update the filter
  if (micros() - microsPrevious >= microsPerReading) {
    microsPrevious = micros(); //reset the micros time counter
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
}



String MagaData()
{ // run over and over
  sensorData = "";
{ while (megaIn.available() > 0) {
      char received = megaIn.read();
      if (received == '\n') //String  sensorData= Serial.readString();
      {
        break;
      }
      sensorData += received ;
    }
    return (String)sensorData;
  }
}


String GetSensorData() {
  String  sensorDatak = "";
  while (megaIn.available())
  { String textMessage = megaIn.readString();
    //Serial.println(textMessage);
    if (megaIn.find("H"))
    {
      while (megaIn.available())
      {
        char inChar = megaIn.read();
        sensorDatak += inChar;
        if (inChar == '\n')
        {
        }       return (String)textMessage;


      }
    }
  }
}
void getAngles(float& roll, float& pitch, float& heading)
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




