byte rows[] = {32,33};
const int rowCount = sizeof(rows)/sizeof(rows[0]);

byte cols[] = {22,23};
const int colCount = sizeof(cols)/sizeof(cols[0]);

byte keys[colCount][rowCount];
byte last_keys[colCount][rowCount];

void setup() {
    Serial.begin(115200);
    for(int x=0; x<rowCount; x++) {
        pinMode(rows[x], INPUT);
    }
    for (int x=0; x<colCount; x++) {
        pinMode(cols[x], INPUT_PULLUP);
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
    readMatrix();
}
