#include <X9C.h>
#include <CmdMessenger.h> 

#define INC 9   // D1 Mini D4 - pulled up in H/W (10k) ->  chip pin 1
#define UD 8   // D1 Mini D8                          ->  chip pin 2
#define CS 10   // D1 Mini D0 - pulled up in H/W (10k) ->  chip pin 7

// "up" and "down" make sense in relation to the wiper pin 5 [VW/RW] and the HIGH end of the pot
// i.e. pin 3 [VH/RH], leaving pin 6 [VL/RL] unused (floating). You can easily use pin 6 instead
// pin 3, but "min" will actually mean "max" and vice versa. Also, the "setPot" percentage will
// set the equivalent of 100-<value>, i.e. setPot(70) will set the resistance between pins 5 and 6
// to 30% of the maximum. (Of course in that case,the "unused" resistance between 5 and 3 will be 70%)
// Nothing to stop you using it as a full centre-tap potentiometer, the above example giving
// pin 3[H] -- 70% -- pin 5[W] -- 30% -- pin 6[L]


X9C pot;                           // create a pot controller

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

// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial,',',';','/');

void attachCommandCallbacks()
{
  cmdMessenger.attach(set_vfd, OnSetVFD);
}

void OnSetVFD() 
{
  int level = cmdMessenger.readBinArg<int>();
  if (level > 255) { level = 255; }
  if (level < 0) { level = 0; }
  int str = (int)((level/255.0)*20.0 + 10);
  pot.setPot(str,true);

  char debug[255];
  sprintf(debug, "Pot level: %d", str);
  cmdMessenger.sendCmd(error, debug);
}

void setup() {
  Serial.begin(9600);
  attachCommandCallbacks();
  pot.begin(CS,INC,UD);
}

void loop() {
  cmdMessenger.feedinSerialData();
}


