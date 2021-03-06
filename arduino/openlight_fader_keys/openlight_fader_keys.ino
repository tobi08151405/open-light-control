byte rows[] = {45,47,49,51};
const int rowCount = sizeof(rows)/sizeof(rows[0]);

byte cols[] = {39,41,43};
const int colCount = sizeof(cols)/sizeof(cols[0]);

byte keys[colCount][rowCount];
byte last_keys[colCount][rowCount];

byte faders[] = {A0, A1, A2};
const byte fadCount = sizeof(faders)/sizeof(faders[0]);

byte fader_motors[][2] = {{38,40},{42,44},{46,48}};

int faderState[fadCount];
int last_faderState[fadCount];

int encCount;
String message;

char delimiter[] = ",";
char *ptr;

const int ledPin = 13;
const int thres = 10;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  pinMode(ledPin, OUTPUT);
//  Serial1.begin(115200);
//  while (!Serial1) {
//    ;
//  }
//  message=Serial1.readStringUntil('\n');
//  encCount = message.toInt();
  for(int x=0; x<rowCount; x++) {
    pinMode(rows[x], INPUT);
  }
  for (int x=0; x<colCount; x++) {
    pinMode(cols[x], INPUT_PULLUP);
  }
  for (int x=0; x<fadCount; x++) {
    for (int y=0; y<2; y++) {
      pinMode(fader_motors[x][y], OUTPUT);
      digitalWrite(fader_motors[x][y], LOW);
    }
  }
}

void readFader() {
  for (int fadIndex=0; fadIndex < fadCount; fadIndex++) {
    int curFad = faders[fadIndex];
    faderState[fadIndex] = analogRead(curFad);
    if (faderState[fadIndex] < 4) {
      faderState[fadIndex] = 0;
    }
    if ((faderState[fadIndex] != last_faderState[fadIndex]) and (((faderState[fadIndex] - thres/2) > last_faderState[fadIndex]) or ((faderState[fadIndex] + thres/2) < last_faderState[fadIndex]))) {
      Serial.print("A"); Serial.print(fadIndex); Serial.print(":"); Serial.println(faderState[fadIndex]);
      last_faderState[fadIndex] = faderState[fadIndex];
    }
  }
}

void setFader(int num, int val) {
  int curFad = faders[num];
  while (true) {
    if (analogRead(curFad) > (val + thres/2)) {
      digitalWrite(fader_motors[num][0], HIGH);
      digitalWrite(fader_motors[num][1], LOW);
    } else if (analogRead(curFad) < (val - thres/2)) {
      digitalWrite(fader_motors[num][0], LOW);
      digitalWrite(fader_motors[num][1], HIGH);
    } else {
      digitalWrite(fader_motors[num][0], LOW);
      digitalWrite(fader_motors[num][1], LOW);
      break;
    }
  }
}

void readSerial() {
  String temp = Serial.readStringUntil(";");
  char string[temp.length()-1];
  temp.toCharArray(string, temp.length()-1);

  String part_string;
  ptr = strtok(string, delimiter);
  part_string = ptr;

  if (string != NULL) {
    while(ptr != NULL) {
      int firstA = part_string.indexOf('A');
      int firstddot = part_string.indexOf(':');
      setFader(part_string.substring(firstA+1, firstddot).toInt(),part_string.substring(firstddot+1).toInt());
      ptr = strtok(NULL, delimiter);
      part_string = ptr;
    }
  }
}

void readMatrix() {
  for (int colIndex=0; colIndex < colCount; colIndex++) {
    byte curCol = cols[colIndex];
    pinMode(curCol, OUTPUT);
    digitalWrite(curCol, LOW);
    for (int rowIndex=0; rowIndex < rowCount; rowIndex++) {
      byte rowCol = rows[rowIndex];
      pinMode(rowCol, INPUT_PULLUP);
      keys[colIndex][rowIndex] = !digitalRead(rowCol);
      if (keys[colIndex][rowIndex] != last_keys[colIndex][rowIndex]) {
        if (keys[colIndex][rowIndex] == HIGH) {
          Serial.print((rowIndex * colCount) + colIndex); Serial.println("1");
          digitalWrite(ledPin, HIGH);
        }
        else {
          Serial.print((rowIndex * colCount) + colIndex); Serial.println("0");
          digitalWrite(ledPin, LOW);
        }
      }
      pinMode(rowCol, INPUT);
    }
    pinMode(curCol, INPUT);
  }
  memcpy(last_keys, keys, sizeof keys);
}

void readEncoders() {
  Serial1.println("get");
  for (int encIndex=0; encIndex<encCount; encIndex++) {
    message = Serial.readStringUntil('\n');
    if (message != "0") {
      Serial.print("E"); Serial.print(encIndex); Serial.print(":"); Serial.println(message);
    }
  }
}

void loop() {
  readFader();
  readMatrix();
  //readEncoders();
  readSerial();
}
