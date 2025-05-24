# Using GIF's For Embedded Animations

## Purpose
 
This project converts GIFs into `.xbm` image frames for use on, but not limited to, 128x64 monochrome OLED displays, such as those controlled by the **ESP32** using the [**U8g2**](#arduino-application) Arduino library.

---


## ImageMagick
__ImageMagick__ is a free, open-source software suite, used for editing and manipulating digital images.

*Link to [ImageMagick's](https://imagemagick.org/index.php) website.*

It's used in this project to resize, crop, clean, and export GIF frames as .xbm files.



[ImageMagick Command Line Options](https://imagemagick.org/script/command-line-options.php)

---

### Check Frame Type

If your GIF uses combine-type frames (where each frame only updates part of the image), the GIF will first need to be converted to replace-type frames. This ensures each frame contains the full image, preventing artifacts like leftover pixels or flickering during playback.

> **Note:** if you plan to use ImageMagick for resizing and cropping, this conversion step is already included — so no need to do it separately.

* Open a CLI in ImageMagick's directory

```bash
magick <INPUT_GIF_PATH> -coalesce -set dispose Background <OUTPUT_GIF_PATH>
```
* Replace `<INPUT_GIF_PATH>` with the path to the GIF you want to use.

* Replace `<OUTPUT_PATH>` with the path to where you want to output the parsed GIF.

### GIF resizing and/or cropping

You'll most likely need to resize and crop your GIF to match the resolution of your display. This can be done using tools like [ImageMagick](#gif-resizing-andor-cropping), GIMP, online GIF editors. etc.

__Recommended Command:__

```bash
magick <INPUT_GIF_PATH> -coalesce -set dispose Background -resize 128x64^ -gravity <POSITION> -extent 128x64 <OUTPUT_PATH>
```

This command prepares, resizes, crops, and pads the input GIF

* Replace `<INPUT_GIF_PATH>` with the path to the GIF you want to use.
* Replace `<POSITION>` with values like center, north, southwest, etc.

  See [ImageMagick gravity options](https://imagemagick.org/script/command-line-options.php#gravity) for all values.
* Replace `<OUTPUT_PATH>` with the path to where you want to output the parsed GIF.

__Command for manual pixel control:__

```bash
magick <INPUT_GIF_PATH> -coalesce -set dispose Background -resize 128x64^ -crop 128x64+<X>+<Y> +repage <OUTPUT_GIF_PATH>
```
* Replace `<INPUT_GIF_PATH>` with the path to the GIF you want to use.

* Replace <X> and <Y> with the appropriate values, where X and Y represent the crop offset from the top-left corner.

* Replace `<OUTPUT_PATH>` with the path to where you want to output the parsed GIF.
---

### Convert GIF Into XBM Frames

To be able to use your GIF as an animation in your arduino code it needs to be broken down into X BitMap (XBM, `.xbm`) frames.

__Recommended Command:__
```bash
magick <INPUT_GIF_PATH> -coalesce -resize <DISPLAY_RES>! -brightness-contrast <BRIGHT_CONT> -background black -extent <DISPLAY_RES> -monochrome -negate +repage "<OUTPUT_PATH>\frame%03d.xbm"
```
* Replace `<INPUT_GIF_PATH>` with the path to the GIF you want to use.

* Replace `<DISPLAY_RES>` with your displays resolution (eg. 128x64).

* Replace `<BRIGHT_CONT>` brightness and contrast values which can be from -100 to 100 (eg. 10x60).

* Replace `<OUTPUT_PATH>` with the path to where you want to output the GIF's frames.

###  Breakdown of the Command
|Part|What It Does|
| - | - |
|-coalesce|Extracts all frames cleanly from animated GIF |
|-resize <DISPLAY_RES>!|Force-resizes to exact display resolution (ignores aspect ratio)|
|-brightness-contrast <BRIGHT_CONT>|controls brightness and contrast levels|
|-background black -extent <DISPLAY_RES>|Adds color (black) padding if resized content is smaller than display resolution|
|-monochrome|Converts to pure black & white (1-bit)|
|-negate|Replaces each pixel with its complementary color (for OLED displays). <br> If your dispay is not OLED you can omit the -negate flag.|
|+repage|Removes any canvas offset metadata|
|frame%03d.xbm|Outputs named frames like frame000.xbm, frame001.xbm, etc.|

> The following configuration has worked well for me:
>```bash
>magick <INPUT_GIF_PATH> -coalesce -resize 128x64! -brightness-contrast 10x60 -background black -extent 128x64 -monochrome -negate +repage "<OUTPUT_PATH>\frame%03d.xbm"
>```
---

### Animation Previewer 

I made a Python tool for previewing how your `.xbm` frames animation looks before uploading to the ESP called `previewer.py`.

If you plan to use the default frame directory, place your `.xbm` frame files in the folder named `frames` inside the tool's directory.

* Open a CLI in the tool's directory location

__Run with:__

```bash
python previewer.py <FRAMES_DIR>
```

* Replace `<FRAMES_DIR>` with the path to the folder containing your frames.

---

## Arduino Application

This project uses the [U8g2 Library](https://github.com/olikraus/u8g2), a versatile monochrome graphics library for embedded systems.

There is some prep work before the frames can be used in your Arduino code.

Unfortunately the code in the `.xbm` frame files produced my ImageMagick isn't compatible with U8g2.

So to make the changes easy I made the following tool.

### U8g2-Compatible Frame Formatter & Header Compiler

I made a Python tool called xbm_frames_to_header.py, it tweaks the code in the `.xbm` frame files so that it is compatible with the U8g2 library, along with compiling them into one `.h` header file to `#include` in your Arduino code to drastically reduce code bloating.

*see [end](#more-details) of U8g2-Compatible Frame Formatter & Header Compiler for more detail of what code is changed.*

#### Preparation

If you plan to use the default frame directory, place your `.xbm` frame files in the folder named `frames` inside the tool's directory.

* Open a CLI in the tool's directory location

__Run with:__

```bash
python XBM_frames2.h.py <FRAMES_DIR> <OUTPUT_FILE>
```
* Replace `<FRAMES_DIR>` with the path to the folder containing your frame files.
* Replace `<OUTPUT_FILE>` with the desired name for the output `.h` file.

* **Note:** You can use a dash (`-`) for either argument to use the default values
  * `frames` folder in this tool's directory

  * `frames.h` as the output file name
---
* After generating the header, copy it into your Arduino project directory and `#include` it in your sketch.

#### More Details

In each `.xbm` code block, the `static char frame000_bits[] = {...}` is changed to `const unsigned char frame000_bits[] PROGMEM = {...}`.<br>This format is required because U8g2 expects frame data as an `unsigned char` array. The `PROGMEM` keyword ensures the data is stored in program memory (flash) rather than RAM, which is important on memory-constrained microcontrollers. At the end of xbm_frames_to_header.py, a `frames[]` array and an integer `totalFrames` are defined.

---
#### Example Code For SH1106 OLED Display:

```ino
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

```