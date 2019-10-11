byte rows[] = {4,5};
const int rowCount = sizeof(rows)/sizeof(rows[0]);

byte cols[] = {2,3};
const int colCount = sizeof(cols)/sizeof(cols[0]);

byte keys[colCount][rowCount];
byte last_keys[colCount][rowCount];

byte faders[] = {A0, A1, A2};
byte fadCount = sizeof(faders)/sizeof(faders[0]);

byte faderState[fadCount];
byte last_faderState[fadCount];

void setup() {
  Serial.begin(115200);
  for(int x=0; x<rowCount; x++) {
    pinMode(rows[x], INPUT);
  }
  for (int x=0; x<colCount; x++) {
    pinMode(cols[x], INPUT_PULLUP);
  }
}

void readFader() {
  for (int fadIndex=0; fadIndex < fadCount; fadIndex++) {
    byte curFad = faders[fadIndex];
    faderState[fadIndex] = analogRead(curFad);
    if (faderState[fadIndex] != last_faderState[fadIndex]) {
      Serial.print("A"); Serial.print(fadIndex); Serial.print(":"); Serial.println(faderState[fadIndex]);
    }
  }
  memcpy(last_faderState, faderState, sizeof fadCount);
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
        }
        else {
          Serial.print((rowIndex * colCount) + colIndex); Serial.println("0");
        }
      }
      pinMode(rowCol, INPUT);
    }
    pinMode(curCol, INPUT);
  }
  memcpy(last_keys, keys, sizeof keys);
}
 
void loop() {
  readFader();
  readMatrix();
}
