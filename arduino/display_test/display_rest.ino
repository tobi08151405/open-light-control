const int clock = 18;
const int data = 19;

byte value[] ={ B00000011, // 0
                B10011111, // 1
                B00100101, // 2
                B00001101, // 3
                B10011001, // 4
                B01001001, // 5
                B01000001, // 6
                B00011111, // 7
                B00000001, // 8
                B00001001, // 9
                B11111111};// display nothing
byte digit[] ={ B00000001, // left segment
                B00000010,
                B00000100,
                B00001000,
                B00010000,
                B00100000,
                B01000000,
                B10000000};

void setup() {
  pinMode(clock, OUTPUT);
  pinMode(data, OUTPUT);
}

void loop() {
 for (int a = 0; a<sizeof(digit); a++){
 for (int i = 0; i<sizeof(value); i++) {
   shiftOut (data, clock, LSBFIRST, value[i]); // delay (5); // NO
   shiftOut (data, clock, LSBFIRST, digit[a]);
   delay (2);
   delay (200);
   shiftOut (data, clock, LSBFIRST, value[i]);
   shiftOut (data, clock, LSBFIRST, digit[a]);
   delay (2);
   delay (100);
   //shiftOut (data, clock, LSBFIRST, value [0]); // delay (5); // NO
   //shiftOut (data, clock, LSBFIRST, digit [2]);
   //delay (2);
 }
 }
}
