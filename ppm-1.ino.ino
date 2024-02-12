/*
 * PPM generator originally written by David Hasko
 * on https://code.google.com/p/generate-ppm-signal/ 
 */

//////////////////////CONFIGURATION///////////////////////////////
#define CHANNEL_NUMBER 12           //set the number of chanels
#define CHANNEL_DEFAULT_VALUE 1500  //set the default servo value
#define FRAME_LENGTH 22500          //set the PPM frame length in microseconds (1ms = 1000µs)
#define PULSE_LENGTH 300            //set the pulse length
#define onState 1                   //set polarity of the pulses: 1 is positive, 0 is negative
#define sigPin 10                   //set PPM signal output pin on the arduino

/*this array holds the servo values for the ppm signal
 change theese values in your code (usually servo values move between 1000 and 2000)
*/
int ppm[CHANNEL_NUMBER];
int new_value = CHANNEL_DEFAULT_VALUE;

unsigned long lastTime = -1;

char buffer[64];
uint8_t idx = 0;
char c;
char *strings[8];
char *ptr = NULL;
byte index = 0;

void setup() {
  
  lastTime = millis();

  Serial.begin(115200);
  Serial.println("[Arduino ppm - Peter Kerney]");
  Serial.println("reset");
  Serial.flush();

  //initiallize default ppm values
  for (int i = 0; i < CHANNEL_NUMBER; i++) {
    ppm[i] = CHANNEL_DEFAULT_VALUE;
  }

  pinMode(sigPin, OUTPUT);
  digitalWrite(sigPin, !onState);  //set the PPM signal pin to the default state (off)

  cli();
  TCCR1A = 0;  // set entire TCCR1 register to 0
  TCCR1B = 0;

  OCR1A = 100;              // compare match register, change this
  TCCR1B |= (1 << WGM12);   // turn on CTC mode
  TCCR1B |= (1 << CS11);    // 8 prescaler: 0,5 microseconds at 16mhz
  TIMSK1 |= (1 << OCIE1A);  // enable timer compare interrupt
  sei();
}


void loop() {

  unsigned long newTime = millis();
  if (newTime-lastTime>5000) { // send a heartbeat every 5 seconds
    Serial.print("t=");
    Serial.println(newTime/1000);
    Serial.flush();
    lastTime=newTime;
  }

  // construct a line from Serial and process it

  int channel = -1;
  int value = -1;

  if (Serial.available()) {
    c = Serial.read();
    buffer[idx++] = c;
  }

  if (c == '\n' || c == '\r') {

    buffer[idx] = 0;
    idx = 0;
    c = 0;

    if (strlen(buffer) > 1) {
      // parse line. It should be "C,V", where C=channel and V=value
      channel = -1;
      value = -1;
      index = 0;
      ptr = strtok(buffer, ",");
      while (ptr != NULL) {
        strings[index] = ptr;
        index++;
        ptr = strtok(NULL, ",");
      }

      channel = atoi(strings[0]);
      value = atoi(strings[1]);

      // reset the strtok() pointers
      ptr = NULL;
      index = 0;

      // ACK the message back to the host
      Serial.print("c=");
      Serial.print(channel);
      Serial.print(",v=");
      Serial.println(value);
      Serial.flush();

      // update the PPM value
      int channelIdx = channel-1;
      if ((channelIdx>=0 && channelIdx<CHANNEL_NUMBER) && (value>=1000 && value<=2000)) {
        ppm[channelIdx]=value;
      } else {
        Serial.println("Invalid");
      }
    }
  }
}

ISR(TIMER1_COMPA_vect) {  //leave this alone
  static boolean state = true;

  TCNT1 = 0;

  if (state) {  //start pulse
    digitalWrite(sigPin, onState);
    OCR1A = PULSE_LENGTH * 2;
    state = false;
  } else {  //end pulse and calculate when to start the next pulse
    static byte cur_chan_numb;
    static unsigned int calc_rest;

    digitalWrite(sigPin, !onState);
    state = true;

    if (cur_chan_numb >= CHANNEL_NUMBER) {
      cur_chan_numb = 0;
      calc_rest = calc_rest + PULSE_LENGTH;  //
      OCR1A = (FRAME_LENGTH - calc_rest) * 2;
      calc_rest = 0;
    } else {
      OCR1A = (ppm[cur_chan_numb] - PULSE_LENGTH) * 2;
      calc_rest = calc_rest + ppm[cur_chan_numb];
      cur_chan_numb++;
    }
  }
}