#include <CmdMessenger.h>  // CmdMessenger

CmdMessenger cmdMessenger = CmdMessenger(Serial);

int hz = 50;
boolean toggle1 = 0;


// Commands
enum
{
  relay_on,
  relay_off,
  set_hz,
  error,
};

void attachCommandCallbacks()
{
  cmdMessenger.attach(set_hz, OnSetHz);
  cmdMessenger.attach(error, OnError);
}

void OnSetHz()
{
  hz = cmdMessenger.readBinArg<int>();
  updateFreq(hz);
}

void OnError()
{
// nop
}

void updateFreq(int freq) {
  cli();//stop interrupts
  
  //set timer1 interrupt at 1Hz
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

void setup() {

  pinMode(7, OUTPUT);

  updateFreq(hz);
  
  // Listen on serial connection for messages from the PC
  // 115200 is the max speed on Arduino Uno, Mega, with AT8u2 USB
  // Use 57600 for the Arduino Duemilanove and others with FTDI Serial
  Serial.begin(57600); 
  
  // Attach my application's user-defined callback methods
  attachCommandCallbacks();   

}

ISR(TIMER1_COMPA_vect){//timer1 interrupt 1Hz toggles pin 13 (LED)
//generates pulse wave of frequency 1Hz/2 = 0.5kHz (takes two cycles for full wave- toggle high then toggle low)
  if (toggle1){
    digitalWrite(7,HIGH);
    toggle1 = 0;
  }
  else{
    digitalWrite(7,LOW);
    toggle1 = 1;
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  cmdMessenger.feedinSerialData();
  // tone(7, hz, 10);
}
