byte direction[] = {2};
const int dirCount = sizeof(direction)/sizeof(direction[0]);
byte pulse[] = {3};

void setup() {
  Serial.begin(9600);
  pinMode(direction, INPUT);
  pinMode(pulse, INPUT);
}

void loop() {
  
}
