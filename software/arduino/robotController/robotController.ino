#define NUM_MOTORS 5
#define STEP_US 40
#define STEP_US_MAX 8 // 8 is the minimum, 20 is good rn
#define STEP_US_SLOW 30
int stepUsMax = STEP_US_MAX;
#define STEP_US_START 60
#define STEP_ACCEL 4
#define WAIT_PER_TURN 0 // 10 to be safe, 30 to be extra safe, none needed
#define STEPS_PER_REV 6400 // maximum amount of microstepping for smoothest operation
#define R 0
#define F 1
#define L 2
#define B 3
#define D 4
#define C 90
#define CC -90
#define C2 180
#define C0 45
#define C1 -45
#define MAX_INPUT 400 // for reading serial

int dirPins[NUM_MOTORS] = {2, 4, 6, 8, 10};
int stepPins[NUM_MOTORS] = {3, 5, 7, 9, 11};

bool movesToDo = false;
String moveString;



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
  
  // if serial data available, process it
  while (Serial.available() > 0)
    processIncomingByte (Serial.read());

  if (movesToDo) {
    moveSequence(moveString);
    movesToDo = false;
  }

  delay(5);

}

void turnMotor(int num, int angle) {
  digitalWrite(dirPins[num], angle > 0 ? LOW : HIGH);
  int stepDelay = STEP_US_START;
  int stepsToMax = (STEP_US_START - stepUsMax)*STEP_ACCEL;
  double stepMax = STEPS_PER_REV*((double) abs(angle)/360.0);
  for (int i = 0; i < stepMax; i++) {
    digitalWrite(stepPins[num], HIGH);
    delayMicroseconds(stepDelay);
    digitalWrite(stepPins[num], LOW);
    delayMicroseconds(stepDelay);
    if (i % STEP_ACCEL == 0 and i < stepsToMax) {
      stepDelay--;
    }
    else if (i % STEP_ACCEL == 0 and i > stepMax-stepsToMax) {
      stepDelay++;
    }
    //Serial.println(stepDelay);
  }
  if (WAIT_PER_TURN>0)
    delay(WAIT_PER_TURN);
}

void turn2Motors(int num1, int angle1, int num2, int angle2) {
  digitalWrite(dirPins[num1], angle1 > 0 ? LOW : HIGH);
  digitalWrite(dirPins[num2], angle2 > 0 ? LOW : HIGH);
  double max1 = STEPS_PER_REV*((double) abs(angle1)/360.0);
  double max2 = STEPS_PER_REV*((double) abs(angle2)/360.0);
  double overallMax = max(max1, max2);
  for (int i = 0; i < overallMax; i++) {
    if (i < max1)
      digitalWrite(stepPins[num1], HIGH);
    if (i < max2)
      digitalWrite(stepPins[num2], HIGH);
    delayMicroseconds(STEP_US);
    if (i < max1)
      digitalWrite(stepPins[num1], LOW);
    if (i < max2)
      digitalWrite(stepPins[num2], LOW);
    delayMicroseconds(STEP_US);
  }
  // when different length moves delay extra long to stop jams
  if (max1 == max2)
    delay(WAIT_PER_TURN);
  else
    delay(WAIT_PER_TURN*2);
}

void moveSequence(String moveString) {
  int numMoves = 0;
  // Move sequence will never be longer than half the max allowed serial input
  // since that input has spaces between every letter
  int moves[MAX_INPUT/2];
  int angles[MAX_INPUT/2];
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
        else if (moveString[i+1] == '0') { // clockwise eighth turn
          angles[numMoves] = C0;
        }
        else if (moveString[i+1] == '1') { // cc eighth turn
          angles[numMoves] = C1;
        }
        else { // clockwise
          angles[numMoves] = C;
        }
      }
      else {
        angles[numMoves] = C;
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
  //Serial.println(numMoves);
  if (numMoves < 5) {
    stepUsMax = STEP_US_SLOW;
  }
  else {
    stepUsMax = STEP_US_MAX;
  }
  // now we have our moves broken down into a form that can be handled by the overloaded moveSequence function
  moveSequence(moves, angles, numMoves);
  Serial.println("Move sequence completed");
}

void moveSequence(int* moves, int* angles, int numMoves) {
  bool did2Motors = false;
  for (int i =0; i < numMoves; i++) {
    // uncomment this to do 2 motors at once
    // skip current instruction if last instruction we did 2 at once
//    if (did2Motors) {
//      did2Motors = false;
//      continue;
//    }
//    // see if we can do 2 turns at once
//    if (i < numMoves-1) {
//      if (abs(moves[i]-moves[i+1]) == 2) {
//        //execute 2 turns at once
//        turn2Motors(moves[i], angles[i], moves[i+1], angles[i+1]);
//        did2Motors = true;
//      }
//    }
    if (!did2Motors) {
      turnMotor(moves[i], angles[i]);
    }
  }
}



// here to process incoming serial data after a terminator received
void process_data (const char * data, int dataLen)
{
  moveString = String(data);
  if (dataLen > 0) {
    movesToDo = true;
  }
    
}  // end of process_data

void processIncomingByte (const byte inByte)
{
  static char input_line [MAX_INPUT];
  static unsigned int input_pos = 0;

  switch (inByte)
  {

    case '\n':   // end of text
      input_line [input_pos] = 0;  // terminating null byte

      // terminator reached! process input_line here ...
      process_data (input_line, input_pos);

      // reset buffer for next time
      input_pos = 0;  
      break;

    case '\r':   // discard carriage return
      break;

    default:
      // keep adding if not full ... allow for terminating null byte
      if (input_pos < (MAX_INPUT - 1))
        input_line [input_pos++] = inByte;
      break;

  }  // end of switch

} // end of processIncomingByte
