#include <U8g2lib.h>   // Include the U8g2 library
#include "frames.h"    // Include the generated header file that defines the frames[] array and totalFrames

// Initialize the U8g2 object for a 128x64 SH1106 display using hardware I2C
// Parameters: rotation, reset pin, clock pin (SCL), data pin (SDA)
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE, /* clock=*/ 9, /* data=*/ 8);

// Set the delay between frames (in milliseconds) to control animation speed
const uint16_t frameDelay = 33; // ~30 FPS
int currentFrame = 0;           // Tracks the current frame index

void setup() {
  u8g2.begin(); // Initialize the display
}

void loop() {
  u8g2.clearBuffer(); // Clear the internal buffer before drawing

  // Draw the current frame at position (0,0) using drawXBMP
  // pgm_read_ptr is used to read the frame pointer from PROGMEM
  u8g2.drawXBMP(0, 0, 128, 64, (const uint8_t*)pgm_read_ptr(&frames[currentFrame]));

  u8g2.sendBuffer(); // Push the buffer to the display

  // Advance to the next frame, wrapping around to 0 at the end
  currentFrame = (currentFrame + 1) % totalFrames;

  delay(frameDelay); // Wait before showing the next frame
}