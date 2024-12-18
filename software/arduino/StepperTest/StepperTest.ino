#define NUM_MOTORS 5
#define DIR_PIN 2
#define STEP_PIN 3
#define DIR_PIN2 4
#define STEP_PIN2 5
#define STEP_US 60 // 8 is the minimum, 20 is good rn
#define WAIT_PER_TURN 40 // 25 is good rn
#define STEPS_PER_REV 6400
#define R 0
#define F 1
#define L 2
#define B 3
#define D 4
#define C 90
#define CC -90
#define C2 180

int dirPins[NUM_MOTORS] = {2, 4, 6, 8, 10};
int stepPins[NUM_MOTORS] = {3, 5, 7, 9, 11};

void setup() {
  Serial.begin(115200);
  // put your setup code here, to run once:
//  pinMode(DIR_PIN, OUTPUT);
//  pinMode(STEP_PIN, OUTPUT);
  for (int i = 0; i < NUM_MOTORS; i++) {
    pinMode(dirPins[i], OUTPUT);
    pinMode(stepPins[i], OUTPUT);
  }
  delay(5000); // delay to plug in power
}

void loop() {
  // sample code for move sequence that uses standard cube algorithm notation
  String moveString = "R L F2 B2 R' L' D' R L F2 B2 R' L' L D' B D' F L' B' R L F2 B2 R' L' D' R L F2 B2 R' L' F R' D F2 R2 D2 F2 D' L2 R L F2 B2 R' L' D R L F2 B2 R' L' D L2";
  Serial.println("CALLING MOVE SEQUENCE");
  moveSequence(moveString);
  delay(10000);
  
//  // sample code for move sequence that uses 2 arrays
//  // T perm: R U R' U' R' F R2 U' R' U' R U R' F' BUT REPLACE U w D and F w B
//  int moves[14] = {R, D, R, D, R, B, R, D, R, D, R, D, R, B};
//  int angles[14] = {C, C, CC, CC, CC, C, C2, CC, CC, CC, C, C, CC, CC};
//  moveSequence(moves, angles, 14);
//  delay(1000);

//  turnMotor(0, -90);
//  turnMotor(1, -90);
//  turnMotor(2, -90);
//  turnMotor(3, -90);
//  turnMotor(4, -90);

//  delay(WAIT_PER_TURN);
//  for (int i = 0; i < 63; i++) {
//  // put your main code here, to run repeatedly:
//  digitalWrite(DIR_PIN, LOW);
//  for (int i = 0; i < STEPS_PER_REV/4; i++) {
//    digitalWrite(STEP_PIN, HIGH);
//    delayMicroseconds(STEP_US);
//    digitalWrite(STEP_PIN, LOW);
//    delayMicroseconds(STEP_US);
//  }
//  delay(WAIT_PER_TURN);
//  digitalWrite(DIR_PIN2, HIGH);
//  for (int i = 0; i < STEPS_PER_REV/4; i++) {
//    digitalWrite(STEP_PIN2, HIGH);
//    delayMicroseconds(STEP_US);
//    digitalWrite(STEP_PIN2, LOW);
//    delayMicroseconds(STEP_US);
//  }
//  delay(WAIT_PER_TURN);
//  }
//  delay(2000);
//  for (int i = 0; i < STEPS_PER_REV/4; i++) {
//    digitalWrite(STEP_PIN, HIGH);
//    delayMicroseconds(STEP_US);
//    digitalWrite(STEP_PIN, LOW);
//    delayMicroseconds(STEP_US);
//  }
//  delay(WAIT_PER_TURN);
//  digitalWrite(DIR_PIN, LOW);
//  for (int i = 0; i < STEPS_PER_REV/4; i++) {
//    digitalWrite(STEP_PIN, HIGH);
//    delayMicroseconds(STEP_US);
//    digitalWrite(STEP_PIN, LOW);
//    delayMicroseconds(STEP_US);
//  }
//  delay(WAIT_PER_TURN);
//  for (int i = 0; i < STEPS_PER_REV/4; i++) {
//    digitalWrite(STEP_PIN, HIGH);
//    delayMicroseconds(STEP_US);
//    digitalWrite(STEP_PIN, LOW);
//    delayMicroseconds(STEP_US);
//  }
//  delay(WAIT_PER_TURN);
}

void turnMotor(int num, int angle) {
  digitalWrite(dirPins[num], angle > 0 ? LOW : HIGH);
  for (int i = 0; i < STEPS_PER_REV*((double) abs(angle)/360.0); i++) {
    digitalWrite(stepPins[num], HIGH);
    delayMicroseconds(STEP_US);
    digitalWrite(stepPins[num], LOW);
    delayMicroseconds(STEP_US);
  }
  delay(WAIT_PER_TURN);
}

void moveSequence(String moveString) {
  int numMoves = 0;
  // assume move sequence will never be 100 moves or longer
  int moves[199];
  int angles[199];
  for (int i = 0; i < moveString.length(); i++) {
    if (moveString[i] == 'R' || moveString[i] == 'F' || moveString[i] == 'D' || moveString[i] == 'L' || moveString[i] == 'B') {
      // get type/direction of move
      if (i < moveString.length()-1) { // to prevent out of bounds
        if (moveString[i+1] == '\'') { // counterclockwise
          angles[numMoves] = CC;
        }
        else if (moveString[i+1] == '2') { // half-turn
          angles[numMoves] = C2;
        }
        else { // clockwise
          angles[numMoves] = C;
        }
      }

      // get cube side
      switch (moveString[i]) {
        case 'R':
          moves[numMoves] = R;
          break;
        case 'F':
          moves[numMoves] = F;
          break;
        case 'D':
          moves[numMoves] = D;
          break;
        case 'L':
          moves[numMoves] = L;
          break;
        case 'B':
          moves[numMoves] = B;
          break;
      }
      numMoves++;
    }
  }
  // now we have our moves broken down into a form that can be handled by the overloaded moveSequence function
  moveSequence(moves, angles, numMoves);
}

void moveSequence(int* moves, int* angles, int numMoves) {
  for (int i =0; i < numMoves; i++) {
    turnMotor(moves[i], angles[i]);
  }
}
