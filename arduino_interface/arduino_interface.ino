/*
 * Interface with Raspberry Pi to play sounds and read sensors * 
 */

#include "Wtv020sd16p.h"

const int RESET_PIN = 4;
const int CLOCK_PIN = 5;
const int DATA_PIN = 6;
const int BUSY_PIN = 7;

Wtv020sd16p sound(RESET_PIN, CLOCK_PIN, DATA_PIN, BUSY_PIN);

void setup() {
  sound.reset();
}

void loop() {
  sound.asyncPlayVoice(0);
  delay(5000);
  sound.stopVoice();
}
