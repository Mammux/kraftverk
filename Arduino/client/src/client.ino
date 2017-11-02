#include <CmdMessenger.h>  // CmdMessenger
#include <SimpleTimer.h>  // SimpleTimer

// #define LIGHT_ARDUINO // OK
// #define BUTTON_ARDUINO // OK
// #define CONTROLS_ARDUINO // OK
// #define WATER_ARDUINO // OK
// #define VFD_ARDUINO // OK
// #define HZ_ARDUINO // OK
// #define DC_VOLT_ARDUINO // OK
// #define DC_AMP_ARDUINO // OK

#if defined(WATER_ARDUINO)
#include <SoftwareSerial.h>
#include <Encoder.h>

Encoder myEnc(4, 5);
long oldPosition = -999;
#endif

#if defined(HZ_ARDUINO)
int hz = 50;
int strength = 128;
boolean toggle1 = 0;
#endif

// Kunne vaert bare for de som trenger
SimpleTimer timer;

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
CmdMessenger cmdMessenger = CmdMessenger(Serial,',',';','/');

// Callbacks define on which received commands we take action 
void attachCommandCallbacks()
{
  cmdMessenger.attach(error, OnError);

#if defined(LIGHT_ARDUINO)
  cmdMessenger.attach(light_on, OnLightOn);
  cmdMessenger.attach(light_off, OnLightOff);
#endif

#if defined(VFD_ARDUINO) || defined(HZ_ARDUINO)
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
  if (light < 5 and light > -1) {
    digitalWrite(8+light, HIGH);
  } else {
    char debug[255];
    sprintf(debug, "Bad light: %d", light);
    cmdMessenger.sendCmd(error, debug);
  }
}

void OnLightOff()
{
  int light = cmdMessenger.readBinArg<int>();
  if (light < 5 and light > -1) {
    digitalWrite(8+light, LOW);
  } else {
    char debug[255];
    sprintf(debug, "Bad light: %d", light);
    cmdMessenger.sendCmd(error, debug);
  }
}
#endif

#if defined(VFD_ARDUINO) || defined(HZ_ARDUINO)
void OnSetVFD() 
{
  int level = cmdMessenger.readBinArg<int>();
  if (level > 255) { level = 255; }
  if (level < 0) { level = 0; }
#if defined(VFD_ARDUINO) 
  analogWrite(6, level);
#else
  strength = level;
#endif
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
    analogWrite(5,strength);
    toggle1 = 0;
  }
  else{
    analogWrite(5,0);
    toggle1 = 1;
  }
}
#endif


void OnError()
{
// nop
}

void sendId()
{
#if defined(BUTTON_ARDUINO)
  cmdMessenger.sendCmdStart(id);
  cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)1);
  cmdMessenger.sendCmdEnd();
#endif	

#if defined(CONTROLS_ARDUINO)
  cmdMessenger.sendCmdStart(id);
  cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)2);
  cmdMessenger.sendCmdEnd();
#endif
}

void updateMsgs()
{
#if defined(BUTTON_ARDUINO)
  handleButton(A0, 3, false);
  handleButton(A1, 2, true);
  handleButton(A2, 0, false);
  handleButton(A3, 1, true);
#endif

#if defined(CONTROLS_ARDUINO)
  handleCtrls();
#endif
}

// Setup function
void setup() 
{

  // Wait for master.py to get ready
  delay(10000);


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

#if defined(HZ_ARDUINO)
  pinMode(5, OUTPUT);
  updateFreq(hz); // starter på 50Hz
#endif

#if defined(BUTTON_ARDUINO)
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
#endif

#if defined(LIGHT_ARDUINO)
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  digitalWrite(8, HIGH);
  digitalWrite(9, HIGH);
  digitalWrite(10, HIGH);
  digitalWrite(11, HIGH);
#endif

#if defined(DC_VOLT_ARDUINO)
  pinMode(12, OUTPUT);
  digitalWrite(12, HIGH);
#endif

#if defined(DC_AMP_ARDUINO)
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
#endif

  // Attach my application's user-defined callback methods
  attachCommandCallbacks();

#if defined(BUTTON_ARDUINO)
  // Should possibly be more frequent?
  timer.setInterval(1000,updateMsgs);
  timer.setInterval(10*1000,sendId);
#endif

#if defined(CONTROLS_ARDUINO)
  timer.setInterval(1000,updateMsgs);
  timer.setInterval(10*1000,sendId);
#endif
}

#if defined(BUTTON_ARDUINO)
void handleButton(uint16_t pin, uint16_t button, bool high) 
{
  int val = analogRead(pin);
  // char debug[255];
  // sprintf(debug, "Debug: bt %d val %d", button, val);
  // cmdMessenger.sendCmd(error, debug);
  if ((val > 512 and high) || (val < 512 and !high)) {
    cmdMessenger.sendCmdStart(button_pressed);
    cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)button);
    cmdMessenger.sendCmdEnd();
  }
}
#endif

#if defined(CONTROLS_ARDUINO)
void handleCtrls()
{
  char debug[255];
  sprintf(debug, "Debug: ctrl a0 %d a1 %d a2 %d a3 %d a4 %d a5 %d", analogRead(A0), analogRead(A1), analogRead(A2), analogRead(A3), analogRead(A4), analogRead(A5));
  cmdMessenger.sendCmd(error, debug);

  // Turbinregulator (0) 0: synker 1: nøytral 2: stiger
  int c_1_a = analogRead(A0);
  int c_1_b = analogRead(A2);
  if (c_1_a > 512 and c_1_b > 512) {
    cmdMessenger.sendCmdStart(control_pos);
    cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)0);
    cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)1);
    cmdMessenger.sendCmdEnd();

  } else if (c_1_a < 512) {
    cmdMessenger.sendCmdStart(control_pos);
    cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)0);
    cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)2);
    cmdMessenger.sendCmdEnd();
  } else {
    cmdMessenger.sendCmdStart(control_pos);
    cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)0);
    cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)0);
    cmdMessenger.sendCmdEnd();
  }
}
#endif

// Loop function
void loop() 
{
  timer.run();
  cmdMessenger.feedinSerialData();
  
// Water arduino looper stramt
#if defined(WATER_ARDUINO)
  long newPosition = myEnc.read();
  if (newPosition != oldPosition) {
  // Håpet er at dette sømløst går over RS485
    long diff = newPosition - oldPosition;
    if (diff >= 5) 
    {
      cmdMessenger.sendCmdStart(control_pos);
      cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)5);
      cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)diff);
      cmdMessenger.sendCmdEnd();
      oldPosition = newPosition;
    }
    if (diff <= -5)
    {
      cmdMessenger.sendCmdStart(control_pos);
      cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)4);
      cmdMessenger.sendCmdBinArg<uint16_t>((uint16_t)-diff);
      cmdMessenger.sendCmdEnd();
      oldPosition = newPosition;
    }

  }
#endif

}


