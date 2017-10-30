#include <CmdMessenger.h>  // CmdMessenger
 
/* 
  Connect 5V on Arduino to VCC on Relay Module
  Connect GND on Arduino to GND on Relay Module 
  Connect GND on Arduino to the Common Terminal (middle terminal) on Relay Module. */

CmdMessenger cmdMessenger = CmdMessenger(Serial);

#define CH1 8
#define CH2 9
#define CH3 10
#define CH4 11
#define CH5 12
#define CH6 13

// Commands
enum
{
  relay_on,
  relay_off,
  error,
};

void attachCommandCallbacks()
{
  cmdMessenger.attach(relay_on, OnRelayOn);
  cmdMessenger.attach(relay_off, OnRelayOff);
  cmdMessenger.attach(error, OnError);
}

void OnRelayOn()
{
  int channel = cmdMessenger.readBinArg<int>();
  if (channel > 6) { channel = 6; }
  if (channel < 1) { channel = 1; }
  if (channel == 1) {
    digitalWrite(CH1, LOW);
  }
  if (channel == 2) {
    digitalWrite(CH2, LOW);
  }
  if (channel == 3) {
    digitalWrite(CH3, LOW);
  }
  if (channel == 4) {
    digitalWrite(CH4, LOW);
  }
  if (channel == 5) {
    digitalWrite(CH5, LOW);
  }
  if (channel == 6) {
    digitalWrite(CH6, LOW);
  }
}

void OnRelayOff()
{
  int channel = cmdMessenger.readBinArg<int>();
  if (channel > 6) { channel = 6; }
  if (channel < 1) { channel = 1; }
  if (channel == 1) {
    digitalWrite(CH1, HIGH);
  }
  if (channel == 2) {
    digitalWrite(CH2, HIGH);
  }
  if (channel == 3) {
    digitalWrite(CH3, HIGH);
  }
  if (channel == 4) {
    digitalWrite(CH4, HIGH);
  }
  if (channel == 5) {
    digitalWrite(CH5, HIGH);
  }
  if (channel == 6) {
    digitalWrite(CH6, HIGH);
  }
}

void OnError()
{
// nop
}
 
void setup(){
  //Setup all the Arduino Pins
  pinMode(CH1, OUTPUT);
  pinMode(CH2, OUTPUT);
  pinMode(CH3, OUTPUT);
  pinMode(CH4, OUTPUT);
  pinMode(CH5, OUTPUT);
  pinMode(CH6, OUTPUT);
  
  //Turn OFF any power to the Relay channels
  digitalWrite(CH1,HIGH);
  digitalWrite(CH2,HIGH);
  digitalWrite(CH3,HIGH);
  digitalWrite(CH4,HIGH);
  digitalWrite(CH5,HIGH);
  digitalWrite(CH6,HIGH);
  
  // Listen on serial connection for messages from the PC
  // 115200 is the max speed on Arduino Uno, Mega, with AT8u2 USB
  // Use 57600 for the Arduino Duemilanove and others with FTDI Serial
  Serial.begin(57600); 
  
  // Attach my application's user-defined callback methods
  attachCommandCallbacks();   
  delay(2000); //Wait 2 seconds before starting sequence
}

void loop(){
 cmdMessenger.feedinSerialData();
}
