#include <CmdMessenger.h>  // CmdMessenger

CmdMessenger cmdMessenger = CmdMessenger(Serial);

int level = 128;

// Commands
enum
{
  relay_on,
  relay_off,
  set_hz,
  vfd_level,
  error,
};

void attachCommandCallbacks()
{
  // arg must be 0 to 255
  cmdMessenger.attach(vfd_level, OnVFDLevel); 
  cmdMessenger.attach(error, OnError);
}

void OnVFDLevel()
{
  level = cmdMessenger.readBinArg<int>();
  if (level > 255) { level = 255; }
  if (level < 0) { level = 0; }
  analogWrite(6, level);
}

void OnError()
{
// nop
}

void setup() {

  pinMode(6, OUTPUT);
 
  // Listen on serial connection for messages from the PC
  // 115200 is the max speed on Arduino Uno, Mega, with AT8u2 USB
  // Use 57600 for the Arduino Duemilanove and others with FTDI Serial
  Serial.begin(57600); 
  
  // Attach my application's user-defined callback methods
  attachCommandCallbacks();   
}

void loop() {
  // put your main code here, to run repeatedly:
  cmdMessenger.feedinSerialData();
}
