byte direction[] = {2};
const int encCount = sizeof(direction)/sizeof(direction[0]);
byte pulse[] = {3};

int curDeriva[encCount];

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);
  for (int encIndex=0; encIndex<encCount; encIndex++) {
    pinMode(direction[encIndex], INPUT);
    pinMode(pulse[encIndex], INPUT);
  }
  while (!Serial) {
    ;
  }
  Serial.println(encCount);
}

void loop() {
  for (int encIndex=0; encIndex<encCount; encIndex++) {
    curValue = digitalRead(pulse[encIndex]);
    if (curValue == HIGH) {
      int currDir = digitalRead(direction[encIndex]);
      if (currDir == HIGH) {
        curDeriva[encIndex] += 1;
      }
      else {
        curDeriva[encIndex] -= 1;
      }
    }
  }
  message = Serial.readStringUntil('\n');
  if (message == "get") {
    for (int encIndex=0; encIndex<encCount; encIndex++) {
      Serial.println(curDeriva[encIndex]);
      curDeriva[encIndex] = 0
    }
  }
}
