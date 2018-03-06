/* 
 * JY901.ino 
 * returns roll, pitch and yaw
 */
 
unsigned char ucDevAddr = 0x50;

#define Roll        0x3d
#define Pitch       0x3e
#define Yaw         0x3f
#define TEMP        0x40

struct SAngle
{
  short Angle[3];
  short T;
};

struct SAngle  jyAngle;
  
void jyBegin()
{
    Wire.begin();
}

void jyGetAngle(short *data)
{
  jyReadRegisters(ucDevAddr, Roll, 6, (char *)data);
}

void jyReadRegisters(unsigned char deviceAddr,unsigned char addressToRead, unsigned char bytesToRead, char * dest)
{
  Wire.beginTransmission(deviceAddr);
  Wire.write(addressToRead);
  Wire.endTransmission(false); //endTransmission but keep the connection active

  Wire.requestFrom(deviceAddr, bytesToRead); //Ask for bytes, once done, bus is released by default

  while(Wire.available() < bytesToRead); //Hang out until we get the # of bytes we expect

  for(int x = 0 ; x < bytesToRead ; x++)
    dest[x] = Wire.read();    
}





