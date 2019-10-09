byte pluses[] = {22,23,12};
const int plusCount = sizeof(pluses)/sizeof(pluses[0]);

byte minuses[] = {32,33,13};
const int minusCount = sizeof(minuses)/sizeof(minuses[0]);

byte leds[plusCount][minusCount];

String message = "";
String mes_new;
int led;
byte led_status;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);
  for(int plus=0; plus<plusCount; plus++) {
    pinMode(pluses[plus], OUTPUT);
    digitalWrite(pluses[plus], LOW);
    for (int minus=0; minus<minusCount; minus++) {
      pinMode(minuses[minus], OUTPUT);
      digitalWrite(minuses[minus], HIGH);
    }
  }
  while (!Serial) {
    ;
  }
}

void loop() {
  message = Serial.readStringUntil('\n');
  mes_new = message[message.length()-1];
  led_status = mes_new.toInt();
  led = message.substring(0, message.length()-1).toInt();
  leds[led/minusCount][led%minusCount];
  Serial.println(led_status);
  Serial.println(led);
  
  for (int plus=0; plus<plusCount; plus++) {
    digitalWrite(pluses[plus], HIGH);
    for (int minus=0; minus<minusCount; minus++) {
      if (leds[plus][minus] == 1) {
        digitalWrite(minuses[minus], LOW);
        delay(10);
        digitalWrite(minuses[minus], HIGH);
      }
    }
    digitalWrite(pluses[plus], LOW);
  }
}
