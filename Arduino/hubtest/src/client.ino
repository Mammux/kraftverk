#include <CmdMessenger.h>  // CmdMessenger
#include <SimpleTimer.h>  // SimpleTimer

#define HUB_ARDUINO 



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
CmdMessenger msgs[] = {
  CmdMessenger(Serial),
  CmdMessenger(Serial1),
  CmdMessenger(Serial2),
  CmdMessenger(Serial3)};

// To Pi

void ForwardButtonPressed()
{
  uint16_t button = msgs[2].readBinArg<uint16_t>();
  Serial.print("forwardButtonPressed");
  Serial.print(button);
}

void ForwardControlPos()
{
  uint16_t control = msgs[3].readBinArg<uint16_t>();
  uint16_t pos = msgs[3].readBinArg<uint16_t>();
  Serial.print("forwardControlPos");
  Serial.print(control);
  Serial.print(pos);
}

// Callbacks define on which received commands we take action 
void attachCommandCallbacks()
{
  msgs[1].attach(Fallback1);

  msgs[2].attach(button_pressed, ForwardButtonPressed);
  msgs[2].attach(Fallback2);

  msgs[3].attach(control_pos, ForwardControlPos);
  msgs[3].attach(Fallback3);
}

void Fallback1()
{
  Serial.println("Fallback2");
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
  if (Serial1.available()) { msgs[1].feedinSerialData(); }
  if (Serial2.available()) { msgs[2].feedinSerialData(); }
  if (Serial3.available()) { msgs[3].feedinSerialData(); }
}


