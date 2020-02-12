#include <TimerOne.h>

#define NCHANN 6
int sensorPins[NCHANN] = {A0,A1,A2,A3,A4,A5};    // input pins for the sensors
int sensorValues[NCHANN];  // list to store the value coming from the sensors

void setup() 
{
  Serial.begin(115200);   
  Timer1.initialize(10000); // 100Hz
  Timer1.attachInterrupt(timerIsr); 
}
 
void loop()
{
}
 

void timerIsr()
{
  for(int i = 0; i < NCHANN; i++) {
    int value = analogRead(sensorPins[i]);
    sensorValues[i] = value;
    Serial.print(sensorValues[i]);
    Serial.print(" ");
  }
  Serial.println();
}
