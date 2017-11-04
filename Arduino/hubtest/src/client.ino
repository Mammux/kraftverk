#include <CmdMessenger.h>  // CmdMessenger

// Commands

enum
{
error,
id,
button_pressed,
control_pos,
light_on,
light_off,
engage_dc_volt,
disengage_dc_volt,
engage_dc_amp,
disengage_dc_amp,
set_vfd,
set_hz
};

// 0 is the raspberry, 1-3 are the other arduinos
// 1: from pi: light_on, light_off, set_vfd, engage_dc_volt, disengage_dc_volt, engage_dc_amp, disengage_dc_amp
// 2: to pi: button_pressed
// 3: to pi: control_pos
// messages from 0 are sent to 1-3, messages from 1-3 are sent to 0
CmdMessenger msgs1 = CmdMessenger(Serial1);
CmdMessenger msgs2 = CmdMessenger(Serial2);
CmdMessenger msgs3 = CmdMessenger(Serial3);


// To Pi

void ForwardButtonPressed()
{
  uint16_t button = msgs2.readBinArg<uint16_t>();
  Serial.print("forwardButtonPressed ");
  Serial.println(button);
}

void ForwardControlPos()
{
  uint16_t control = msgs3.readBinArg<uint16_t>();
  uint16_t pos = msgs3.readBinArg<uint16_t>();
  Serial.print("forwardControlPos ");
  Serial.print(control);
  Serial.print(" ");
  Serial.println(pos);
}

void Error1()
{
  char* msg = msgs1.readStringArg();
  Serial.print("error1: ");
  Serial.println(msg);
}


void Error2()
{
  char* msg = msgs2.readStringArg();
  Serial.print("error2: ");
  Serial.println(msg);
}


void Error3()
{
  char* msg = msgs3.readStringArg();
  Serial.print("error3: ");
  Serial.println(msg);
}


void Id1()
{
  uint16_t id = msgs1.readBinArg<uint16_t>();
  Serial.print("id1: ");
  Serial.println(id);
}

void Id2()
{
  uint16_t id = msgs2.readBinArg<uint16_t>();
  Serial.print("id2: ");
  Serial.println(id);
}

void Id3()
{
  uint16_t id = msgs3.readBinArg<uint16_t>();
  Serial.print("id3: ");
  Serial.println(id);
}


// Callbacks define on which received commands we take action 
void attachCommandCallbacks()
{
  msgs1.attach(Fallback1);
  msgs1.attach(id, Id1);
  msgs1.attach(error, Error1);

  msgs2.attach(button_pressed, ForwardButtonPressed);
  msgs2.attach(Fallback2);
  msgs2.attach(id, Id2);
  msgs2.attach(error, Error2);

  msgs3.attach(control_pos, ForwardControlPos);
  msgs3.attach(Fallback3);
  msgs3.attach(id, Id3);
  msgs3.attach(error, Error3);
}

void Fallback1()
{
  Serial.println("Fallback1");
}

void Fallback2()
{
  Serial.println("Fallback2");
}

void Fallback3()
{
  Serial.println("Fallback3");
}

// Setup function
void setup() 
{
  // Wait for master.py to get ready
  delay(5000);

  // Listen on serial connection for messages from the PC
  // 115200 is the max speed on Arduino Uno, Mega, with AT8u2 USB
  // Use 57600 for the Arduino Duemilanove and others with FTDI Serial
  Serial.begin(57600); 
  Serial1.begin(57600);
  Serial2.begin(57600);
  Serial3.begin(57600);

  // Attach my application's user-defined callback methods
  attachCommandCallbacks();
}

// Loop function
void loop() 
{
  if (Serial1.available()) { msgs1.feedinSerialData(); }
  if (Serial2.available()) { msgs2.feedinSerialData(); }
  if (Serial3.available()) { msgs3.feedinSerialData(); }
}


