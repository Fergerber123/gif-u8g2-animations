import os
import sys
import re

# Handle arguments
args = sys.argv[1:]
FRAME_DIR = "./frames"
OUTPUT_FILE = "frames.h"

if len(args) >= 1 and args[0] != "-":
    FRAME_DIR = args[0]

if len(args) >= 2 and args[1] != "-":
    OUTPUT_FILE = args[1]


# --- Header file preamble ---
header = "#pragma once\n\n"

frames = []
frame_names = []

# --- Parse all .xbm files ---
for filename in sorted(os.listdir(FRAME_DIR)):
    if filename.endswith(".xbm"):
        path = os.path.join(FRAME_DIR, filename)
        with open(path, "r") as f:
            content = f.read()

            # Find the array name
            match = re.search(r"\b(char|unsigned char)\s+(\w+)\s*\[\]", content)
            if not match:
                print(f"Warning: Could not find array declaration in {filename}")
                continue

            name = match.group(2)
            frame_names.append(name)

            # Replace declaration with correct format
            content = re.sub(
                r"\b(char|unsigned char)\s+(\w+)\s*\[\]",
                r"const unsigned char \2[] PROGMEM",
                content
            )

            # Remove #define lines
            lines = content.splitlines()
            lines = [line for line in lines if not line.startswith("#define")]
            frames.append("\n".join(lines))

# --- Write to header file ---
with open(OUTPUT_FILE, "w") as f:
    f.write(header)
    f.write("\n\n".join(frames))
    f.write("\n\nconst unsigned char* const frames[] PROGMEM = {\n")
    for name in frame_names:
        f.write(f"  {name},\n")
    f.write("};\n")
    f.write(f"const int totalFrames = {len(frame_names)};\n")

print(f"Generated {OUTPUT_FILE} with {len(frame_names)} frames.")
