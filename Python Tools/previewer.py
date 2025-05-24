import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

# --- Get frames directory from command-line argument or default ---
if len(sys.argv) > 1:
    FRAME_DIR = sys.argv[1]
else:
    FRAME_DIR = "./frames"  # default folder if no argument given

FRAME_DELAY = 100  # milliseconds per frame

root = tk.Tk()
root.title("XBM Animation Preview")

# Load frames after root initialized
frames = []
for filename in sorted(os.listdir(FRAME_DIR)):
    if filename.lower().endswith(".xbm"):
        path = os.path.join(FRAME_DIR, filename)
        img = Image.open(path).convert("1")
        frames.append(ImageTk.BitmapImage(img))

label = tk.Label(root, image=frames[0])
label.pack()

frame_index = 0

def update_frame():
    global frame_index
    label.config(image=frames[frame_index])
    frame_index = (frame_index + 1) % len(frames)
    root.after(FRAME_DELAY, update_frame)

update_frame()
root.mainloop()
