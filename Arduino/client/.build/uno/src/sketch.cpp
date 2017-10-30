#include <Arduino.h>
#include <CmdMessenger.h>  // CmdMessenger
void attachCommandCallbacks();
void OnSetVoltage();
void OnError();
void setup();
void loop();
#line 1 "src/sketch.ino"
//#include <CmdMessenger.h>  // CmdMessenger

#define voltmeterPin 3
#define ledPin 13
// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial);

// Commands
enum
{
  set_voltage,
  error,
};

// Callbacks define on which received commands we take action 
void attachCommandCallbacks()
{
  cmdMessenger.attach(set_voltage, OnSetVoltage);
  cmdMessenger.attach(error, OnError);
}

// Callback function that sets led on or off
void OnSetVoltage()
{
  // Read led state argument, interpret string as boolean
  int voltage = cmdMessenger.readBinArg<int>();
  if (voltage > 255) { voltage = 255; }
  if (voltage < 0) { voltage = 0; }
  analogWrite(voltmeterPin, voltage);
  analogWrite(ledPin, voltage);
}

void OnError()
{
// nop
}

// Setup function
void setup() 
{

  pinMode(voltmeterPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  // Listen on serial connection for messages from the PC
  // 115200 is the max speed on Arduino Uno, Mega, with AT8u2 USB
  // Use 57600 for the Arduino Duemilanove and others with FTDI Serial
  Serial.begin(57600); 

  // Attach my application's user-defined callback methods
  attachCommandCallbacks();

}

// Loop function
void loop() 
{
  // Process incoming serial data, and perform callbacks
  cmdMessenger.feedinSerialData();
}


