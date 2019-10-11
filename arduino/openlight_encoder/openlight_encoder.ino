byte direction[] = {2};
const int dirCount = sizeof(direction)/sizeof(direction[0]);
byte pulse[] = {3};

int curValue[dirCount];
int lastValue[dirCount];

void setup() {
  Serial.begin(9600);
  for (int dirIndex=0; dirIndex<dirCount; dirIndex++) {
    pinMode(direction[dirIndex], INPUT);
    pinMode(pulse[dirIndex], INPUT);
  }
}

void loop() {
  for (int dirIndex=0; dirIndex<dirCount; dirIndex++) {
    
  }
}
