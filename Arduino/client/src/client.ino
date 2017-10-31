#include <CmdMessenger.h>  // CmdMessenger

#define LIGHT_ARDUINO // OK
#define BUTTON_ARDUINO // OK
// #define CONTROLS_ARDUINO // OK
// #define WATER_ARDUINO // OK
// #define VFD_ARDUINO // OK
// #define HZ_ARDUINO // OK
#define DC_VOLT_ARDUINO // OK
#define DC_AMP_ARDUINO // OK

#if defined(WATER_ARDUINO)
#include <SoftwareSerial.h>
#include <Encoder.h>

Encoder myEnc(4, 5);
long oldPosition = -999;
#endif

#if defined(HZ_ARDUINO)
int hz = 50;
boolean toggle1 = 0;
#endif

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

// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial);

// Callbacks define on which received commands we take action 
void attachCommandCallbacks()
{
  cmdMessenger.attach(error, OnError);

#if defined(LIGHT_ARDUINO)
  cmdMessenger.attach(light_on, OnLightOn);
  cmdMessenger.attach(light_off, OnLightOff);
#endif

#if defined(VFD_ARDUINO)
  cmdMessenger.attach(set_vfd, OnSetVFD);
#endif

#if defined(HZ_ARDUINO)
  cmdMessenger.attach(set_hz, OnSetHz);
#endif

#if defined(DC_VOLT_ARDUINO)
  cmdMessenger.attach(engage_dc_volt, OnEngageDCVolt);
  cmdMessenger.attach(disengage_dc_volt, OnDisengageDCVolt);
#endif

#if defined(DC_AMP_ARDUINO)
  cmdMessenger.attach(engage_dc_amp, OnEngageDCAmp);
  cmdMessenger.attach(disengage_dc_amp, OnDisengageDCAmp);
#endif

}

#if defined(DC_VOLT_ARDUINO)
void OnEngageDCVolt()
{
  digitalWrite(12, LOW);  
}

void OnDisengageDCVolt()
{
  digitalWrite(12, HIGH);  
}
#endif

#if defined(DC_AMP_ARDUINO)
void OnEngageDCAmp()
{
  digitalWrite(13, LOW);  
}

void OnDisengageDCAmp()
{
  digitalWrite(13, HIGH);  
}
#endif


#if defined(LIGHT_ARDUINO)
void OnLightOn()
{
  int light = cmdMessenger.readBinArg<int>();
  if (light < 5 & light > -1) {
    digitalWrite(8+light, HIGH);
  } else {
    cmdMessenger.sendCmd(error);
  }
}

void OnLightOff()
{
  int light = cmdMessenger.readBinArg<int>();
  if (light < 5 & light > -1) {
    digitalWrite(8+light, LOW);
  } else {
    cmdMessenger.sendCmd(error);
  }
}
#endif

#if defined(VFD_ARDUINO)
void OnSetVFD() 
{
  int level = cmdMessenger.readBinArg<int>();
  if (level > 255) { level = 255; }
  if (level < 0) { level = 0; }
  analogWrite(6, level);
}
#endif

#if defined(HZ_ARDUINO)
void OnSetHz() 
{
  hz = cmdMessenger.readBinArg<int>();
  updateFreq(hz);
}

void updateFreq(int freq) {
  cli();//stop interrupts
  
  //set timer1 interrupt at (hz) Hz (approximately)
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;//initialize counter value to 0
  // set compare match register for 1hz increments
  OCR1A = int(15624 / (hz*2));// = (16*10^6) / (1*1024) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12 and CS10 bits for 1024 prescaler
  TCCR1B |= (1 << CS12) | (1 << CS10);  
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);
  
  sei();//allow interrupts
}

ISR(TIMER1_COMPA_vect){
// TODO: klarer vi å få denne til å være lenger / kortere HIGH avhengig av volum?
  if (toggle1){
    digitalWrite(7,HIGH);
    toggle1 = 0;
  }
  else{
    digitalWrite(7,LOW);
    toggle1 = 1;
  }
}
#endif


void OnError()
{
// nop
}

// Setup function
void setup() 
{
  // Listen on serial connection for messages from the PC
  // 115200 is the max speed on Arduino Uno, Mega, with AT8u2 USB
  // Use 57600 for the Arduino Duemilanove and others with FTDI Serial
#if defined(WATER_ARDUINO)
  Serial.begin(2400); // Slow (safe) RS485
#else
  Serial.begin(57600); 
#endif

#if defined(VFD_ARDUINO)
  pinMode(6, OUTPUT);
#endif

#if defined(LIGHT_ARDUINO)
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
#endif

#if defined(DC_VOLT_ARDUINO)
  pinMode(12, OUTPUT);
#endif

#if defined(DC_AMP_ARDUINO)
  pinMode(13, OUTPUT);
#endif

#if defined(HZ_ARDUINO)
  pinMode(7, OUTPUT);
  updateFreq(hz); // starter på 50Hz
#endif

  // Attach my application's user-defined callback methods
  attachCommandCallbacks();

}

#if defined(BUTTON_ARDUINO)
void handleButton(int pin, int button, bool high) 
{
  int val = analogRead(pin);
  if ((val > 512 & high) | (val < 512 & !high)) {
    cmdMessenger.sendCmd(button_pressed, button);
  }
}
#endif

#if defined(CONTROLS_ARDUINO)
void handleCtrls()
{
  // Turbinregulator (0) 0: synker 1: nøytral 2: stiger
  int c_1_a = analogRead(A0);
  int c_1_b = analogRead(A2);
  if (c_1_a > 512 & c_1_b > 512) {
    cmdMessenger.sendCmd(control_pos, 0, 1);
  } else if (c_1_a < 512) {
    cmdMessenger.sendCmd(control_pos, 0, 2);
  } else {
    cmdMessenger.sendCmd(control_pos, 0, 0);
  }
}
#endif

// Loop function
void loop() 
{
#if defined(LIGHT_ARDUINO) || defined(VFD_ARDUINO)
  cmdMessenger.feedinSerialData();
#endif
  
#if defined(BUTTON_ARDUINO)
  cmdMessenger.sendCmdStart(id);
  cmdMessenger.sendCmdArg<uint16_t>((uint16_t)1);
  cmdMessenger.sendCmdEnd();
  handleButton(A0, 3, false);
  handleButton(A1, 2, true);
  handleButton(A2, 0, false);
  handleButton(A3, 1, true);
#endif

#if defined(CONTROLS_ARDUINO)
  cmdMessenger.sendCmdStart(id);
  cmdMessenger.sendCmdArg<uint16_t>((uint16_t)2);
  cmdMessenger.sendCmdEnd();
  handleCtrls();
#endif

// Water arduino looper stramt
#if defined(WATER_ARDUINO)
  long newPosition = myEnc.read();
  if (newPosition != oldPosition) {
  // Håpet er at dette sømløst går over RS485
    cmdMessenger.sendCmdStart(control_pos);
    cmdMessenger.sendCmdArg<uint16_t>((uint16_t)4);
    cmdMessenger.sendCmdArg<uint16_t>((uint16_t)newPosition - oldPosition);
    cmdMessenger.sendCmdEnd();
    oldPosition = newPosition;
  }
#endif

// M� erstatte dette med noe som f�lger med p� hvor lenge det er siden vi sist sendte "status"

#if defined(BUTTONS_ARDUINO) || defined(CONTROLS_ARDUINO)
  delay(1000);
#endif
}


